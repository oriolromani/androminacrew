from django.contrib import admin

from .models import Company, CustomUser

admin.site.register(Company)


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_company")


admin.site.register(CustomUser, UserAdmin)
