from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from erp_project import settings

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),  # ← KIRITING
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("inventory/", include("inventory.urls")),
    path("sales/", include("sales.urls")),
    path("", include("dashboard.urls")),  # bosh sahifa
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
)

if settings.DEBUG:
    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
