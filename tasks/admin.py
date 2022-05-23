from django.contrib import admin

from .models import Gig, Task, WorkTime

admin.site.register(Gig)
admin.site.register(Task)
admin.site.register(WorkTime)
