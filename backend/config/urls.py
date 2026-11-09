from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from . import views as config_views

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("presentation/", config_views.presentation, name="presentation"),
    path("healthz/", config_views.healthz, name="healthz"),
    path("manifest.json", config_views.serve_static_file, {"filename": "manifest.json"}, name="manifest"),
    path("sw.js", config_views.serve_static_file, {"filename": "sw.js"}, name="sw"),
    path("robots.txt", config_views.serve_static_file, {"filename": "robots.txt"}, name="robots"),
    path("sitemap.xml", config_views.serve_static_file, {"filename": "sitemap.xml"}, name="sitemap"),
    path("api/", config_views.api_index, name="api-index"),
    path("api/v1/", config_views.api_index, name="api-index-v1"),
    # SPA routes with language prefix (for refresh/bookmark support)
    path("<str:lang>/", TemplateView.as_view(template_name="index.html"), name="spa-home"),
    path("<str:lang>/<str:view>/", TemplateView.as_view(template_name="index.html"), name="spa-view"),
    path("<str:lang>/<str:view>/<str:sub>/", TemplateView.as_view(template_name="index.html"), name="spa-sub"),
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/wallet/", include("wallet.urls")),
    path("api/v1/logistics/", include("logistics.urls")),
    path("api/v1/customs/", include("customs.urls")),
    path("api/v1/blockchain/", include("blockchain.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
