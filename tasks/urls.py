from django.urls import path

from tasks import views

urlpatterns = [
    path("", views.TaskList.as_view(), name="tasks"),
    path("<uid>/", views.TaskDetail.as_view(), name="task"),
    path(
        "<uid>/work-time-creation/",
        views.WorkTimeCreation.as_view(),
        name="work_time_creation",
    ),
    path(
        "<uid>/work-time/<pk>/", views.WorkTimeDetail.as_view(), name="work_time_detail"
    ),
]
