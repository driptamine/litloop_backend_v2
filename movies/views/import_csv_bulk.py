import csv
from datetime import datetime
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from movies.models import Movie, WatchlistItem, ImdbMovie
from users.models import User

@csrf_exempt
def import_watchlist_csv(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    user = request.user  # Make sure user is authenticated

    csv_file = request.FILES.get('csv_file')
    if not csv_file or not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'CSV file required'}, status=400)

    decoded = csv_file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))

    movies_to_create = []
    watchlist_to_create = []

    existing_movie_ids = set(ImdbMovie.objects.values_list('imdb_id', flat=True))
    existing_watchlist = set(
        WatchlistItem.objects.filter(user=user)
        .values_list('movie__imdb_id', flat=True)
    )

    def parse_date(s):
        try:
            return datetime.strptime(s, '%Y-%m-%d').date()
        except:
            return None

    for row in reader:
        imdb_id = row.get('Const')
        if not imdb_id:
            continue

        # 1. Create or prepare Movie
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
                created_at=parse_date(row.get('Created')),
                modified_at=parse_date(row.get('Modified')),
            )
            movies_to_create.append(movie)

    # Bulk create movies first
    ImdbMovie.objects.bulk_create(movies_to_create, ignore_conflicts=True)
    all_movies = {m.imdb_id: m for m in ImdbMovie.objects.filter(imdb_id__in=[row['Const'] for row in reader])}

    csv_file.seek(0)
    next(reader)  # skip header

    for row in reader:
        imdb_id = row.get('Const')
        if not imdb_id or imdb_id in existing_watchlist:
            continue

        movie = all_movies.get(imdb_id)
        if not movie:
            continue

        watchlist = WatchlistItem(
            user=user,
            movie=movie,
            user_rating=float(row['Your Rating']) if row.get('Your Rating') else None,
            date_rated=parse_date(row.get('Date Rated')),
        )
        watchlist_to_create.append(watchlist)

    WatchlistItem.objects.bulk_create(watchlist_to_create, ignore_conflicts=True)

    return JsonResponse({
        'status': 'success',
        'movies_imported': len(movies_to_create),
        'watchlist_items_imported': len(watchlist_to_create)
    })
