import requests
from imdb import Cinemagoer
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from movies.models import Movie, ImdbMovie, MovieView
from movies.utils import tmdb as tmdb_utils


@shared_task
def increment_view(user_id, movie_id):
    try:
        user = User.objects.get(pk=user_id)
        movie = Movie.objects.get(tmdb_id=movie_id)
    except ObjectDoesNotExist:
        return

    if MovieView.objects.filter(user=user, movie=movie).exists():
        return

    view = MovieView(user=user, movie=movie)
    view.save()


@shared_task
def scrape_tmdb_movie(tmdb_id):
    data = tmdb_utils.get_movie(tmdb_id)
    if not data:
        return {"error": f"TMDB movie {tmdb_id} not found"}

    title = data.get("title", "")
    description = data.get("overview", "")
    poster = data.get("poster_path")
    if poster:
        poster = f"https://image.tmdb.org/t/p/w500{poster}"
    backdrop = data.get("backdrop_path")
    if backdrop:
        backdrop = f"https://image.tmdb.org/t/p/w1280{backdrop}"

    imdb_id = tmdb_utils.extract_imdb_id(data)
    imdb_id_int = int(imdb_id) if imdb_id and imdb_id.isdigit() else None

    movie, _ = Movie.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "imdb_id": imdb_id_int,
            "title": title,
            "description": description,
            "movie_file": backdrop or "",
            "poster": poster or "",
        }
    )
    if not _:
        changed = False
        if imdb_id_int and movie.imdb_id != imdb_id_int:
            movie.imdb_id = imdb_id_int; changed = True
        if title and movie.title != title:
            movie.title = title; changed = True
        if description and movie.description != description:
            movie.description = description; changed = True
        if backdrop and movie.movie_file != backdrop:
            movie.movie_file = backdrop; changed = True
        if poster and movie.poster != poster:
            movie.poster = poster; changed = True
        if changed:
            movie.save()

    if imdb_id:
        directors_list = tmdb_utils.extract_directors(data)
        directors = ", ".join(directors_list) if directors_list else ""
        genres = tmdb_utils.extract_genres(data)
        release_date = tmdb_utils.extract_release_date(data)
        year = tmdb_utils.extract_year(data)
        runtime = data.get("runtime")
        vote_average = data.get("vote_average")
        vote_count = data.get("vote_count")

        ImdbMovie.objects.get_or_create(
            imdb_id=imdb_id,
            defaults={
                "title": title,
                "original_title": data.get("original_title", ""),
                "title_type": "movie",
                "imdb_rating": vote_average,
                "runtime_minutes": runtime,
                "year": year,
                "release_date": release_date,
                "genres": genres,
                "num_votes": vote_count,
                "directors": directors,
                "description": description,
            }
        )

    return {"tmdb_id": tmdb_id, "title": title, "imdb_id": imdb_id}


@shared_task
def scrape_tmdb_popular(page=1):
    data = tmdb_utils.get_popular(page)
    if not data:
        return {"error": "Failed to fetch popular movies"}

    results = data.get("results", [])
    tmdb_ids = [item["id"] for item in results if item.get("id")]

    tasks = []
    for tid in tmdb_ids:
        task = scrape_tmdb_movie.delay(tid)
        tasks.append(task.id)

    return {"page": page, "enqueued": len(tasks), "task_ids": tasks}


@shared_task
def create_or_update_movie():
    items = []
    imdb_ids = []
    url = 'http://api.themoviedb.org/3/movie/popular?api_key=bceb6c0fefae8ee5a3cf9762ec780d63&page=1'
    api_url = "https://api.themoviedb.org/3/movie/"
    cinemagoer = Cinemagoer()

    response = requests.get(url).json()

    for item in response['results']:
        item_id = item.get('id')
        items.append(item_id)

    for tmdb_id in items:
        url = f"{api_url}{tmdb_id}/external_ids?api_key=bceb6c0fefae8ee5a3cf9762ec780d63"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(f"Data for tmdb-ID {tmdb_id}:")
            imdb_id = data.get('imdb_id')
            print(data.get('imdb_id'))

            imdb_id = imdb_id.replace('tt', '')
            movie = cinemagoer.get_movie(imdb_id)

            title = movie.get('title')
            plot = movie.get('plot')

            movie = Movie(
                tmdb_id=tmdb_id,
                title=title,
                description=plot,
                imdb_id=imdb_id
            )
            movie.save()
        else:
            print(f"Error retrieving data for ID {id}: {response.status_code}")
