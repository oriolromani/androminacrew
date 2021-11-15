from django.urls import path

from tasks import views

urlpatterns = [
    path("", views.TaskList.as_view(), name="tasks"),
    path("<uid>/", views.TaskDetail.as_view(), name="task"),
]
