from django.core.management.base import BaseCommand, CommandError
from movies.tasks import scrape_tmdb_movie, scrape_tmdb_popular


class Command(BaseCommand):
    help = "Scrape movie data from TMDB into Movie and ImdbMovie models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tmdb-id",
            type=int,
            help="Scrape a single movie by TMDB ID",
        )
        parser.add_argument(
            "--popular",
            type=int,
            nargs="?",
            const=1,
            default=None,
            help="Scrape popular movies (optionally specify page number)",
        )

    def handle(self, *args, **options):
        tmdb_id = options.get("tmdb_id")
        popular = options.get("popular")

        if tmdb_id:
            self.stdout.write(f"Scraping TMDB movie {tmdb_id}...")
            result = scrape_tmdb_movie(tmdb_id)
            self.stdout.write(self.style.SUCCESS(f"Done: {result}"))
        elif popular is not None:
            page = popular if popular else 1
            self.stdout.write(f"Scraping popular TMDB movies page {page}...")
            result = scrape_tmdb_popular(page=page)
            self.stdout.write(self.style.SUCCESS(f"Done: {result}"))
        else:
            raise CommandError("Specify --tmdb-id or --popular")
