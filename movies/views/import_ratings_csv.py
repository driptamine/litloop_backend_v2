import csv
import io
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from movies.models import ImdbMovie, ImdbMovieRating
from users.auth_utils import jwt_required


@csrf_exempt
@jwt_required
def import_ratings_csv(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    user = request.user
    csv_file = request.FILES.get('csv_file')
    if not csv_file or not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'CSV file required'}, status=400)

    try:
        decoded = csv_file.read().decode('utf-8')
        rows = list(csv.DictReader(io.StringIO(decoded)))

        def parse_date(s):
            try:
                return datetime.strptime(s, '%Y-%m-%d').date()
            except:
                return None

        existing_ids = set(ImdbMovie.objects.values_list('imdb_id', flat=True))
        movies_to_create = []
        new_imdb_ids = set()

        for row in rows:
            imdb_id = row.get('Const')
            if not imdb_id:
                continue

            if imdb_id not in existing_ids and imdb_id not in new_imdb_ids:
                movies_to_create.append(ImdbMovie(
                    imdb_id=imdb_id,
                    title=row.get('Title') or '',
                    url=row.get('URL') or '',
                    title_type=row.get('Title Type') or '',
                    imdb_rating=float(row['IMDb Rating']) if row.get('IMDb Rating') else None,
                    runtime_minutes=int(row['Runtime (mins)']) if row.get('Runtime (mins)') else None,
                    year=int(row['Year']) if row.get('Year') else None,
                    genres=row.get('Genres') or '',
                    num_votes=int(row['Num Votes']) if row.get('Num Votes') else None,
                    release_date=parse_date(row.get('Release Date')),
                    directors=row.get('Directors') or '',
                ))
                new_imdb_ids.add(imdb_id)

        ratings_created = 0
        ratings_updated = 0

        with transaction.atomic():
            ImdbMovie.objects.bulk_create(movies_to_create, ignore_conflicts=True)

            all_ids = existing_ids | new_imdb_ids
            movies_map = {
                m.imdb_id: m
                for m in ImdbMovie.objects.filter(imdb_id__in=all_ids)
            }

            for row in rows:
                imdb_id = row.get('Const')
                if not imdb_id:
                    continue

                movie = movies_map.get(imdb_id)
                if not movie:
                    continue

                your_rating = float(row['Your Rating']) if row.get('Your Rating') else None
                date_rated = parse_date(row.get('Date Rated'))
                if your_rating is None and date_rated is None:
                    continue

                _, created = ImdbMovieRating.objects.update_or_create(
                    user=user,
                    imdb_movie=movie,
                    defaults={
                        'rating': your_rating,
                        'date_rated': date_rated,
                    },
                )
                if created:
                    ratings_created += 1
                else:
                    ratings_updated += 1

        return JsonResponse({
            'status': 'success',
            'movies_imported': len(movies_to_create),
            'ratings_created': ratings_created,
            'ratings_updated': ratings_updated,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
