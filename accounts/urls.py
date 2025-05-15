from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
)

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/del", UserDeleteView.as_view(), name="user_delete"),
]
