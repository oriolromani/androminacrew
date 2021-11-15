from django.contrib import admin

from .models import Task, WorkTime

admin.site.register(Task)
admin.site.register(WorkTime)
