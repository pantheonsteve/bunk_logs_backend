from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token

User = get_user_model()

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Return CSRF token for JavaScript clients
    """
    token = get_token(request)
    return JsonResponse({'detail': 'CSRF cookie set', 'csrfToken': token})

def get_auth_status(request):
    """
    Return authentication status and user info
    """
    if request.user.is_authenticated:
        response_data = {
            'isAuthenticated': True,
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'username': getattr(request.user, 'username', request.user.email),
                'name': getattr(request.user, 'name', ''),
                'role': request.user.role,
                # Add other user fields you want to expose
            }
        }
        
        # Add bunk information for counselors
        if request.user.role == 'Counselor':
            # Get assigned bunks for the counselor
            bunks = list(request.user.assigned_bunks.filter(is_active=True).values(
                'id', 'cabin__name', 'session__name'
            ))
            
            # Format the bunks for the response
            formatted_bunks = []
            for bunk in bunks:
                formatted_bunks.append({
                    'id': bunk['id'],
                    'name': f"{bunk['cabin__name']} - {bunk['session__name']}"
                })
                
            response_data['user']['bunks'] = formatted_bunks
            
        return JsonResponse(response_data)
    else:
        return JsonResponse({
            'isAuthenticated': False,
        })