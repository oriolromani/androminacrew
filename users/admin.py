from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Company, CustomUser

admin.site.register(Company)


class UserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_company", "uid")


admin.site.register(CustomUser, UserAdmin)
