from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Company, CustomUser, Invitation

admin.site.register(Company)


class UserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_company")


admin.site.register(CustomUser, UserAdmin)


class InvitationAdmin(admin.ModelAdmin):
    list_display = ("company", "user", "status", "created")


admin.site.register(Invitation, InvitationAdmin)
