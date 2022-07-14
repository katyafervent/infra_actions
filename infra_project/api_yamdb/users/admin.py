from django.conf import settings
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Custom admin panel for user."""
    list_display = (
        'pk',
        'email',
        'first_name',
        'bio',
        'role',
    )
    search_fields = ('first_name', 'email')
    list_filter = ('role',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
