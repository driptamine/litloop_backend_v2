

class AdType(TimeStampedModel, models.Model):

    """
    A type of advertisement including such parameters as the amount of text and images size.

    Many ad types are industry standards from the Interactive Advertising Bureau (IAB).
    Some publishers prefer native ads that are custom sized for their needs.

    See https://www.iab.com/newadportfolio/
    """

    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)

    # image specifications
    # image_height/width of null means it accepts any value (not recommended)
    has_image = models.BooleanField(_("Has image?"), default=True)
    image_width = models.PositiveIntegerField(blank=True, null=True)
    image_height = models.PositiveIntegerField(blank=True, null=True)

    # text specifications
    has_text = models.BooleanField(_("Has text?"), default=True)
    max_text_length = models.PositiveIntegerField(
        blank=True, null=True, help_text=_("Max length does not include HTML tags")
    )

    # Deprecated - new ads don't allow any HTML
    # They are instead broken into a headline, body, and call to action
    allowed_html_tags = models.CharField(
        _("Allowed HTML tags"),
        blank=True,
        max_length=255,
        default="a b strong i em code",
        help_text=_("Space separated list of allowed HTML tag names"),
    )

    default_enabled = models.BooleanField(
        default=False,
        help_text=_(
            "Whether this ad type should default to checked when advertisers are creating ads"
        ),
    )

    template = models.TextField(
        _("Ad template"),
        blank=True,
        null=True,
        help_text=_("Override the template for rendering this ad type"),
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("A short description of the ad type to guide advertisers."),
    )
    order = models.PositiveSmallIntegerField(default=0)

    deprecated = models.BooleanField(
        default=False,
        help_text=_(
            "Users cannot select deprecated ad types unless an ad is already that type."
        ),
    )

    publisher_groups = models.ManyToManyField(
        PublisherGroup,
        related_name="adtypes",
        blank=True,
        help_text=_(
            "This is used for ad types specific to certain publishers. "
            "By default, an ad type is global for all publishers.",
        ),
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        """Simple override."""
        return self.name

        
class Advertisement(TimeStampedModel, IndestructibleModel):

    """
    A single advertisement creative.

    Multiple ads are organized into a :py:class:`~Flight` which has details
    common across the ad such as targeting and desired number of clicks.

    At this level, we store:

    * The HTML for the ad
    * An optional image to go with the ad
    * The display type of the ad (footer, sidebar, etc.)
    * Whether the ad is "live"
    * The link to the advertisers landing page

    Since ads contain important historical data around tracking how we bill
    and report to customers, they cannot be deleted once created.
    """

    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)

    # ad.text used to be a standalone field with certain HTML supported
    # Now it is constructed from the headline, content, and call to action
    # Headline, content, and CTA do not allow any HTML
    text = models.TextField(
        _("Text"),
        blank=True,
        help_text=_("For most ad types, the text should be less than 100 characters."),
    )
    headline = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_(
            "An optional headline at the beginning of the ad usually displayed in bold"
        ),
    )
    content = models.TextField(
        blank=True,
        null=True,
        help_text=_(
            "For most ad types, the combined length of the headline, body, and call to action "
            "should be less than 100 characters."
        ),
    )
    cta = models.CharField(
        _("Call to action"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_(
            "An optional call to action displayed at the end of the ad usually in bold"
        ),
    )

    # Supports simple variables like ${publisher} and ${advertisement}
    # using string.Template syntax
    link = models.URLField(
        _("Link URL"),
        max_length=255,
        help_text=_(
            "URL of your landing page. "
            "This may contain UTM parameters so you know the traffic came from us. "
            "The publisher will be added in the 'ea-publisher' query parameter."
        ),
    )
    image = models.FileField(
        _("Image"),
        max_length=255,
        upload_to="images/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Sized according to the ad type"),
    )
    live = models.BooleanField(_("Live"), default=False)
    flight = models.ForeignKey(
        Flight, related_name="advertisements", on_delete=models.PROTECT
    )

    # Deprecated - this will be removed
    ad_type = models.ForeignKey(
        AdType, blank=True, null=True, default=None, on_delete=models.PROTECT
    )

    ad_types = models.ManyToManyField(
        AdType,
        related_name="advertisements",
        blank=True,
        help_text=_("Possible ways this ad will be displayed"),
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ("slug", "-live")

    def __copy__(self):
        """Duplicate an ad."""
        # https://docs.djangoproject.com/en/3.2/topics/db/queries/#copying-model-instances
        # Get a fresh reference so that "self" doesn't become the new copy
        ad = Advertisement.objects.get(pk=self.pk)

        # Get a slug that doesn't already exist
        new_slug = ad.slug + "-copy"
        while Advertisement.objects.filter(slug=new_slug).exists():
            new_slug += "-" + get_random_string(3)

        ad_types = ad.ad_types.all()

        ad.pk = None
        ad.name += " Copy"
        ad.slug = new_slug
        ad.live = False  # The new ad should always be non-live
        ad.save()

        ad.ad_types.set(ad_types)
        return ad

    def __str__(self):
        """Simple override."""
        return self.name

    def get_absolute_url(self):
        return reverse(
            "advertisement_detail",
            kwargs={
                "advertiser_slug": self.flight.campaign.advertiser.slug,
                "flight_slug": self.flight.slug,
                "advertisement_slug": self.slug,
            },
        )

    def incr(self, impression_type, publisher):
        """
        Add to the number of times this action has been performed, stored in the DB.

        TODO: Refactor this method, moving it off the Advertisement class since it can be called
              without an advertisement when we have a Decision and no Offer.
        """
        day = get_ad_day().date()

        if isinstance(impression_type, str):
            impression_types = (impression_type,)
        else:
            impression_types = impression_type

        for imp_type in impression_types:
            assert imp_type in IMPRESSION_TYPES

            # Update the denormalized fields on the Flight
            if imp_type == VIEWS:
                Flight.objects.filter(pk=self.flight_id).update(
                    total_views=models.F("total_views") + 1
                )
            elif imp_type == CLICKS:
                Flight.objects.filter(pk=self.flight_id).update(
                    total_clicks=models.F("total_clicks") + 1
                )

        # Ensure that an impression object exists for today
        # and make sure to query the writable DB for this
        impression, created = AdImpression.objects.using("default").get_or_create(
            advertisement=self,
            publisher=publisher,
            date=day,
            defaults={imp_type: 1 for imp_type in impression_types},
        )

        if not created:
            # If the object was created above, we don't need to update
            # since the defaults will have already done the update for us.
            AdImpression.objects.using("default").filter(pk=impression.pk).update(
                **{imp_type: models.F(imp_type) + 1 for imp_type in impression_types}
            )

    def _record_base(
        self, request, model, publisher, keywords, url, div_id, ad_type_slug
    ):
        """
        Save the actual AdBase model to the database.

        This is used for all subclasses,
        so we need to keep all the data passed in generic.
        """
        ip_address = get_client_ip(request)
        user_agent = get_client_user_agent(request)
        client_id = get_client_id(request)
        parsed_ua = parse(user_agent)
        country = get_client_country(request)
        url = url or request.META.get("HTTP_REFERER")

        if model != Click and settings.ADSERVER_DO_NOT_TRACK:
            # For compliance with DNT,
            # we can't store UAs indefinitely from a user merely browsing
            user_agent = None

        if div_id:
            # Even though the publisher could have a div of any length
            # and we want to echo back the same div to them,
            # we only store the first 100 characters of it.
            div_id = div_id[: Offer.DIV_MAXLENGTH]

        obj = model.objects.create(
            date=timezone.now(),
            publisher=publisher,
            ip=anonymize_ip_address(ip_address),
            user_agent=user_agent,
            client_id=client_id,
            country=country,
            url=url,
            # Derived user agent data
            browser_family=parsed_ua.browser.family,
            os_family=parsed_ua.os.family,
            is_bot=parsed_ua.is_bot,
            is_mobile=parsed_ua.is_mobile,
            # Client Data
            keywords=keywords if keywords else None,  # Don't save empty lists
            div_id=div_id,
            ad_type_slug=ad_type_slug,
            # Page info
            advertisement=self,
        )
        return obj

    def track_impression(self, request, impression_type, publisher, offer):
        if impression_type not in (CLICKS, VIEWS):
            raise RuntimeError("Impression must be either a click or a view")

        if impression_type == CLICKS:
            self.track_click(request, publisher, offer)
        elif impression_type == VIEWS:
            self.track_view(request, publisher, offer)

    def track_click(self, request, publisher, offer):
        """Store click data in the DB."""
        self.incr(impression_type=CLICKS, publisher=publisher)
        return self._record_base(
            request=request,
            model=Click,
            publisher=publisher,
            keywords=offer.keywords,
            url=offer.url,
            div_id=offer.div_id,
            ad_type_slug=offer.ad_type_slug,
        )

    def track_view(self, request, publisher, offer):
        """
        Store view data in the DB.

        Views are only stored if ``settings.ADSERVER_RECORD_VIEWS=True``
        or a publisher has the ``Publisher.record_views`` flag set.
        For a large scale ad server, writing a database record per ad view
        is not feasible
        """
        self.incr(impression_type=VIEWS, publisher=publisher)

        if request.GET.get("uplift"):
            # Don't overwrite Offer object here, since it might have changed prior to our writing
            Offer.objects.filter(pk=offer.pk).update(uplifted=True)

        if settings.ADSERVER_RECORD_VIEWS or publisher.record_views:
            return self._record_base(
                request=request,
                model=View,
                publisher=publisher,
                keywords=offer.keywords,
                url=offer.url,
                div_id=offer.div_id,
                ad_type_slug=offer.ad_type_slug,
            )

        log.debug("Not recording ad view.")
        return None

    def track_view_time(self, offer, view_time):
        """Store the time the ad was in view."""
        # Don't overwrite the Offer object here, it might have changed prior to our writing
        if view_time > Offer.MAX_VIEW_TIME:
            # Set a maximum allowed view time so averages aren't thrown off
            view_time = Offer.MAX_VIEW_TIME
            log.warning("View time exceeded maximum view time: view_time=%s", view_time)
        if (
            not offer.is_old()
            and offer.viewed
            and not offer.view_time
            and view_time > 0
        ):
            Offer.objects.filter(pk=offer.pk).update(view_time=view_time)
            return True

        log.info("View time was for an invalid view")
        return False

    def offer_ad(
        self, request, publisher, ad_type_slug, div_id, keywords, url=None, forced=False
    ):
        """
        Offer to display this ad on a specific publisher and a specific display (ad type).

        Tracks an offer in the database to save data about it and compare against view.
        """
        ad_type = AdType.objects.filter(slug=ad_type_slug).first()

        self.incr(impression_type=(OFFERS, DECISIONS), publisher=publisher)
        offer = self._record_base(
            request=request,
            model=Offer,
            publisher=publisher,
            keywords=keywords,
            url=url,
            div_id=div_id,
            ad_type_slug=ad_type_slug,
        )

        if forced and self.flight.campaign.campaign_type == PAID_CAMPAIGN:
            # Ad offers forced to a specific ad or campaign should never be billed.
            # By discarding the nonce, the ad view/click will never count.
            # We will still record data for unpaid campaign in reporting though.
            nonce = "forced"
        else:
            nonce = offer.pk

        view_url = generate_absolute_url(
            reverse("view-proxy", kwargs={"advertisement_id": self.pk, "nonce": nonce})
        )

        view_time_url = generate_absolute_url(
            reverse(
                "view-time-proxy", kwargs={"advertisement_id": self.pk, "nonce": nonce}
            )
        )

        click_url = generate_absolute_url(
            reverse("click-proxy", kwargs={"advertisement_id": self.pk, "nonce": nonce})
        )

        text = self.render_links(click_url)
        body = html.unescape(bleach.clean(text, tags=[], strip=True))

        return {
            "id": self.slug,
            "text": text,
            "body": body,
            "html": self.render_ad(
                ad_type, click_url=click_url, view_url=view_url, publisher=publisher
            ),
            # Breakdown of the ad text into its component parts
            "copy": {
                "headline": self.headline or "",
                "cta": self.cta or "",
                "content": self.content or body,
            },
            "image": self.image.url if self.image else None,
            "link": click_url,
            "view_url": view_url,
            "view_time_url": view_time_url,
            "nonce": nonce,
            "display_type": ad_type_slug,
            "campaign_type": self.flight.campaign.campaign_type,
        }

    @classmethod
    def record_null_offer(cls, request, publisher, ad_type_slug, div_id, keywords, url):
        """
        Store null offers, so that we can keep track of our fill rate.

        Without this, when we don't offer an ad and a user doesn't have house ads on,
        we don't have any way to track how many requests for an ad there have been.
        """
        cls.incr(self=None, impression_type=DECISIONS, publisher=publisher)
        cls._record_base(
            self=None,
            request=request,
            model=Offer,
            publisher=publisher,
            keywords=keywords,
            url=url,
            div_id=div_id,
            ad_type_slug=ad_type_slug,
        )

    def is_valid_offer(self, impression_type, offer):
        """
        Returns true if this nonce (from ``offer_ad``) is valid for a given impression type.

        A nonce is valid if it was generated recently (hasn't timed out)
        and hasn't already been used.
        """
        if offer.is_old():
            return False

        if impression_type == VIEWS:
            return offer.viewed is False
        if impression_type == CLICKS:
            return offer.viewed is True and offer.clicked is False

        return False

    def invalidate_nonce(self, impression_type, nonce):
        if impression_type == VIEWS:
            Offer.objects.filter(id=nonce).update(viewed=True)
        if impression_type == CLICKS:
            Offer.objects.filter(id=nonce).update(clicked=True)

    def view_ratio(self, day=None):
        if not day:
            day = get_ad_day()
        impression = self.impressions.get_or_create(date=day)[0]
        return impression.view_ratio

    def click_ratio(self, day=None):
        if not day:
            day = get_ad_day()
        impression = self.impressions.get_or_create(date=day)[0]
        return impression.click_ratio

    def clicks_today(self, day=None):
        return self.clicks_shown_today(day)

    def clicks_shown_today(self, day=None):
        if not day:
            day = get_ad_day()
        impression = self.impressions.get_or_create(date=day)[0]
        return float(impression.clicks)

    def views_shown_today(self, day=None):
        if not day:
            day = get_ad_day()
        impression = self.impressions.get_or_create(date=day)[0]
        return float(impression.views)

    def total_views(self):
        aggregate = self.impressions.aggregate(models.Sum("views"))["views__sum"]
        if aggregate:
            return aggregate
        return 0

    def total_clicks(self):
        aggregate = self.impressions.aggregate(models.Sum("clicks"))["clicks__sum"]
        if aggregate:
            return aggregate
        return 0

    def ctr(self):
        return calculate_ctr(self.total_clicks(), self.total_views())

    def country_click_breakdown(self, start_date, end_date=None):
        report = Counter()

        clicks = self.clicks.filter(date__gte=start_date)
        if end_date:
            clicks = clicks.filter(date__lte=end_date)

        for click in clicks:
            country = "Unknown"

            if click.country:
                country = str(click.country.name)
            report[country] += 1

        return report

    def render_links(self, link=None):
        """
        Include the link in the html text.

        Does not include any callouts such as "ads served ethically"
        """
        url = link or self.link
        if not self.text:
            template = get_template("adserver/advertisement-body.html")
            ad_html = template.render(
                {
                    "ad": self,
                }
            ).strip()
        else:
            ad_html = self.text

        return mark_safe(
            ad_html.replace(
                "<a>", '<a href="%s" rel="nofollow noopener" target="_blank">' % url
            )
        )

    def render_ad(self, ad_type, click_url=None, view_url=None, publisher=None):
        """Render the ad as HTML including any proxy links for collecting view/click metrics."""
        if not ad_type:
            # Render by the first ad type for this ad
            # This is only used to preview the ad
            ad_type = self.ad_types.all().first()

        if ad_type and ad_type.template:
            # Check if the ad type has a specific template
            template = engines["django"].from_string(ad_type.template)
        else:
            # Otherwise get the default template
            # Don't do this by default as searching for a template is expensive
            template = get_template("adserver/advertisement.html")

        return template.render(
            {
                "ad": self,
                "publisher": publisher,
                "image_url": self.image.url if self.image else None,
                "link_url": click_url or self.link,
                "view_url": view_url,
                "text_as_html": self.render_links(link=click_url),
            }
        ).strip()
