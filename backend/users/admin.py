from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow

admin.site.register(Follow)


@admin.register(User)
class UserAdmin(UserAdmin):
    search_fields = ('username', 'email')
