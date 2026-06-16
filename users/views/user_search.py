from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_GET
from users.models import User

@require_GET
def user_search_api(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
        
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).distinct()[:50]  # Limit to 50 results
    
    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar,
            'is_verified': user.is_verified,
        })
        
    return JsonResponse({
        'query': query,
        'count': len(user_data),
        'results': user_data
    })
