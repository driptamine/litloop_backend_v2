import requests
from django.conf import settings
from datetime import datetime

TMDB_API_BASE = "https://api.themoviedb.org/3"


def api_key():
    return settings.TMDB_API_KEY


def get_movie(tmdb_id):
    url = f"{TMDB_API_BASE}/movie/{tmdb_id}?api_key={api_key()}&append_to_response=external_ids,credits"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.json()


def get_popular(page=1):
    url = f"{TMDB_API_BASE}/movie/popular?api_key={api_key()}&page={page}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.json()


def extract_imdb_id(data):
    ext = data.get("external_ids", {}) or {}
    imdb = ext.get("imdb_id") or data.get("imdb_id")
    if imdb:
        return imdb.replace("tt", "")
    return None


def extract_directors(data):
    credits = data.get("credits", {}) or {}
    crew = credits.get("crew", [])
    return [c["name"] for c in crew if c.get("job") == "Director"]


def extract_genres(data):
    genres = data.get("genres", []) or []
    return ", ".join(g["name"] for g in genres)


def extract_release_date(data):
    raw = data.get("release_date")
    if raw:
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def extract_year(data):
    raw = data.get("release_date")
    if raw and len(raw) >= 4:
        try:
            return int(raw[:4])
        except ValueError:
            return None
    return None
