from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from faqs.views import home_page_view

urlpatterns = [
    path("", home_page_view, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("faqs.urls")),  # API endpoints
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
