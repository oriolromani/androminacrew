from django.urls import path

from users import views

urlpatterns = [
    path("", views.UsersList.as_view(), name="users"),
    path("detail/", views.UserDetail.as_view(), name="user_detail"),
    path("api-token-auth/", views.CustomObtainToken.as_view(), name="api_token_auth"),
]
