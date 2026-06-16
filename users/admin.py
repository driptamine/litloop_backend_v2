from django.contrib import admin
from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'username')
    list_filter = ('is_verified', 'is_staff', 'is_active')
    ordering = ('-created_at',)
