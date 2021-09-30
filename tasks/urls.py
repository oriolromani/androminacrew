from django.urls import path

from tasks import views

urlpatterns = [
    path("tasks/", views.TaskList.as_view(), name="tasks"),
    path("assign_task/", views.CreateUserTask.as_view(), name="user_tasks"),
]
