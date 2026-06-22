"""URL configuration for the TTombo web project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Bisa — administração"
admin.site.site_title = "Bisa"
admin.site.index_title = "Transcrição de manuscritos"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]

# Serve uploaded manuscript images in development. In production Caddy serves
# MEDIA_URL directly from MEDIA_ROOT.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
