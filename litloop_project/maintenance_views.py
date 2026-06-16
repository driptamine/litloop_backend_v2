from django.core.management import call_command
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class DeleteAllTablesView(View):
    """
    GET /maintenance/delete-tables/
    WARNING: This will drop all tables in the public schema.
    """
    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DROP SCHEMA public CASCADE;")
                cursor.execute("CREATE SCHEMA public;")
                cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                db_user = settings.DATABASES['default']['USER']
                cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user};")
            
            return JsonResponse({
                'status': 'success',
                'message': 'All tables have been deleted. You must run the regenerate endpoint now.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete tables: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RegenerateAllView(View):
    """
    GET /maintenance/regenerate/
    Runs all migrations to recreate the database schema.
    """
    def get(self, request, *args, **kwargs):
        try:
            call_command('migrate', interactive=False)
            return JsonResponse({
                'status': 'success',
                'message': 'Database tables have been regenerated successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to regenerate database: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DeleteUserTablesView(View):
    """
    GET /maintenance/delete-user-tables/
    Drops only the User related tables and clears their migration history.
    """
    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                # List of tables likely associated with the 'users' app
                tables_to_drop = [
                    'users_user_groups',
                    'users_user_user_permissions',
                    'users_user',
                ]
                for table in tables_to_drop:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                
                # Clear migration history for 'users' app so it can be migrated again
                cursor.execute("DELETE FROM django_migrations WHERE app = 'users';")
            
            return JsonResponse({
                'status': 'success',
                'message': 'User tables have been deleted and migration history cleared.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete user tables: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RegenerateUserTablesView(View):
    """
    GET /maintenance/regenerate-user-tables/
    Runs migrations specifically for the 'users' app.
    """
    def get(self, request, *args, **kwargs):
        try:
            call_command('migrate', 'users', interactive=False)
            return JsonResponse({
                'status': 'success',
                'message': 'User tables have been regenerated successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to regenerate user tables: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DeleteChatTablesView(View):
    """
    GET /maintenance/delete-chat-tables/
    Drops only the Chat related tables and clears their migration history.
    """
    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                # List of tables likely associated with the 'chats' app
                tables_to_drop = [
                    'chats_messagevideo',
                    'chats_messagephoto',
                    'chats_messagetrack',
                    'chats_message',
                    'chats_chat_participants',
                    'chats_chat',
                ]
                for table in tables_to_drop:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                
                # Clear migration history for 'chats' app so it can be migrated again
                cursor.execute("DELETE FROM django_migrations WHERE app = 'chats';")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Chat tables have been deleted and migration history cleared.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete chat tables: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RegenerateChatTablesView(View):
    """
    GET /maintenance/regenerate-chat-tables/
    Runs migrations specifically for the 'chats' app.
    """
    def get(self, request, *args, **kwargs):
        try:
            call_command('migrate', 'chats', interactive=False)
            return JsonResponse({
                'status': 'success',
                'message': 'Chat tables have been regenerated successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to regenerate chat tables: {str(e)}'
            }, status=500)
