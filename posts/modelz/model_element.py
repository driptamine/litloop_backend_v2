# REFERENCE: https://github.com/Lomascolo/django-media-explorer/blob/cbced4d552c47710ed6889fb217a59304e1bebc4/media_explorer/models.py#L75

class Element(models.Model):
    """
    The Element model will contain images and videos
    NOTE: if type=video you can still have a thumbnail_image
    """

    TYPE_CHOICES = (('image','Image'),('video','Video'))

    name = models.CharField(max_length=150,blank=True,null=True)
    file_name = models.CharField(max_length=150,blank=True,null=True)
    original_file_name = models.CharField(max_length=150,blank=True,null=True)
    credit = models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    image = models.FileField(blank=True,null=True,max_length=255,upload_to="images/")
    image_url = models.CharField(max_length=255,blank=True,null=True)
    image_width = models.IntegerField(blank=True,null=True,default='0')
    image_height = models.IntegerField(blank=True,null=True,default='0')
    video_url = models.CharField(max_length=255,blank=True,null=True)
    video_embed = models.TextField(blank=True,null=True)
    manual_embed_code = models.BooleanField(_("Manually enter video embed code"), default=False)
    thumbnail_image = models.FileField(blank=True,null=True,max_length=255,upload_to="images/")
    thumbnail_image_url = models.CharField(max_length=255,blank=True,null=True)
    thumbnail_image_width = models.IntegerField(blank=True,null=True,default='0')
    thumbnail_image_height = models.IntegerField(blank=True,null=True,default='0')
    type = models.CharField(_("Type"), max_length=10, default="image",choices=TYPE_CHOICES)
    created_at = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    updated_at = models.DateTimeField(blank=True,null=True,auto_now=True)

class Gallery(models.Model):

    elements = models.ManyToManyField(Element, through="GalleryElement")

class GalleryElement(models.Model):
    gallery = models.ForeignKey(Gallery)
    element = models.ForeignKey(Element)
