# movies/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from users.models import User
from movies.models import WatchlistItem

from users.auth_utils import jwt_required  # 👈 your decorator

@jwt_required
def user_watchlist_api(request, user_id):

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Check: Only allow the authenticated user to see their own watchlist
    if request.user.id != user_id:
        return JsonResponse({"error": "Forbidden"}, status=403)

    user = get_object_or_404(User, id=user_id)

    # Pagination
    try:
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))
    except ValueError:
        return JsonResponse({"error": "Invalid pagination parameters"}, status=400)

    if page < 1 or per_page < 1:
        return JsonResponse({"error": "Page and per_page must be positive integers."}, status=400)

    watchlist_qs = (
        WatchlistItem.objects.filter(user=user)
        .select_related('movie')
        .order_by('-movie__created_at')
    )

    total_items = watchlist_qs.count()
    total_pages = (total_items + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    watchlist_page = watchlist_qs[start:end]

    watchlist_data = [
        {
            "movie_id": item.movie.id,
            "title": item.movie.title,
            "imdb_created_at": item.movie.created_at.isoformat() if item.movie.created_at else None
        }
        for item in watchlist_page
    ]

    return JsonResponse({
        "user_id": user.id,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "watchlist": watchlist_data
    })
