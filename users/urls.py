from django.urls import path

from users import views

urlpatterns = [
    path("", views.UsersList.as_view(), name="users"),
    path("confirmed/", views.CompanyUsersList.as_view(), name="confirmed_users"),
]
