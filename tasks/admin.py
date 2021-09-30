from django.contrib import admin

from .models import Task, UserTask, WorkTime

admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(WorkTime)
