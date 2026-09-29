from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ==============================================================================
# Django Admin Panel Sozlamalari (Professional Branding)
# ==============================================================================
admin.site.site_header = "UNG | Quduqlar qurulishi bo'yicha"
admin.site.site_title = "UNG Drilling"
admin.site.index_title = "Tizim Ma'lumotnomalari va Boshqaruv Paneli"
admin.site.empty_value_display = "— yo'q —"

urlpatterns = [
    # Bosh sahifani admin panelga yo'naltirish
    path('', RedirectView.as_view(url='/admin/', permanent=False)),

    # Django Admin paneli
    path('admin/', admin.site.urls),

    # OpenAPI 3.0 Schema va Swagger / ReDoc hujjatlari
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # REST API v1 (Ma'lumotnomalar va Operatsiyalar)
    path('api/v1/', include('apps.directory.urls')),
    path('api/v1/', include('apps.operations.urls')),
]
