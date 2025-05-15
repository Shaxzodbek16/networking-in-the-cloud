# inventory/urls.py
from django.urls import path
from .views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/new/", CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit", CategoryUpdateView.as_view(), name="category_update"
    ),
    path(
        "categories/<int:pk>/del", CategoryDeleteView.as_view(), name="category_delete"
    ),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/new/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/del", ProductDeleteView.as_view(), name="product_delete"),
]
