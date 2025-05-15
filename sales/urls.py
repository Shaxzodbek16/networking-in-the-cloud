from django.urls import path
from .views import SaleListView, SaleCreateView, SaleDetailView

urlpatterns = [
    path("", SaleListView.as_view(), name="sale_list"),
    path("new/", SaleCreateView.as_view(), name="sale_create"),
    path("<int:pk>/", SaleDetailView.as_view(), name="sale_detail"),
]
