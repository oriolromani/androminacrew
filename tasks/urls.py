from django.urls import path

from tasks import views

urlpatterns = [
    path("", views.TaskList.as_view(), name="tasks"),
    path("create_task/", views.CreateUserTask.as_view(), name="user_tasks"),
]
