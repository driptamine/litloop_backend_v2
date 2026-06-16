import csv
import io
from datetime import datetime

from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from movies.models import Movie, WatchlistItem, ImdbMovie
from users.models import User
from users.auth_utils import jwt_required


@csrf_exempt
@jwt_required
def import_watchlist_csv(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    user = request.user

    csv_file = request.FILES.get('csv_file')
    if not csv_file or not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'CSV file required'}, status=400)

    try:
        decoded = csv_file.read().decode('utf-8')
        rows = list(csv.DictReader(io.StringIO(decoded)))

        movies_to_create = []
        watchlist_to_create = []

        existing_movie_ids = set(ImdbMovie.objects.values_list('imdb_id', flat=True))
        existing_watchlist_ids = set(
            WatchlistItem.objects.filter(user=user).values_list('movie__imdb_id', flat=True)
        )

        def parse_date(s):
            try:
                return datetime.strptime(s, '%Y-%m-%d').date()
            except:
                return None

        def parse_datetime(s):
            try:
                dt = datetime.strptime(s, '%Y-%m-%d')
                return make_aware(dt)
            except:
                return None

        for row in rows:
            imdb_id = row.get('Const')
            if not imdb_id:
                continue

            if imdb_id not in existing_movie_ids:
                movie = ImdbMovie(
                    imdb_id=imdb_id,
                    title=row.get('Title') or '',
                    original_title=row.get('Original Title') or '',
                    url=row.get('URL') or '',
                    title_type=row.get('Title Type') or '',
                    imdb_rating=float(row['IMDb Rating']) if row.get('IMDb Rating') else None,
                    runtime_minutes=int(row['Runtime (mins)']) if row.get('Runtime (mins)') else None,
                    year=int(row['Year']) if row.get('Year') else None,
                    genres=row.get('Genres') or '',
                    num_votes=int(row['Num Votes']) if row.get('Num Votes') else None,
                    release_date=parse_date(row.get('Release Date')),
                    directors=row.get('Directors') or '',
                    description=row.get('Description') or '',
                    created_at=parse_datetime(row.get('Created')),
                    modified_at=parse_datetime(row.get('Modified')),
                )
                movies_to_create.append(movie)

        with transaction.atomic():
            ImdbMovie.objects.bulk_create(movies_to_create, ignore_conflicts=True)

            # Get all movies again
            imdb_ids = [row['Const'] for row in rows if row.get('Const')]
            all_movies = {
                m.imdb_id: m for m in ImdbMovie.objects.filter(imdb_id__in=imdb_ids)
            }

            for row in rows:
                imdb_id = row.get('Const')
                if not imdb_id or imdb_id in existing_watchlist_ids:
                    continue

                movie = all_movies.get(imdb_id)
                if not movie:
                    continue

                watchlist_item = WatchlistItem(
                    user=user,
                    movie=movie,
                    user_rating=float(row['Your Rating']) if row.get('Your Rating') else None,
                    date_rated=parse_date(row.get('Date Rated')),
                )
                watchlist_to_create.append(watchlist_item)

            WatchlistItem.objects.bulk_create(watchlist_to_create, ignore_conflicts=True)

        return JsonResponse({
            'status': 'success',
            'movies_imported': len(movies_to_create),
            'watchlist_items_imported': len(watchlist_to_create)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
