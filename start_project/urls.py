"""start_project URL Configuration."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView)

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index),

    # Authentication module
    path('user/', include('authentication.urls.user_urls')),
    path('employee/', include('authentication.urls.employee_urls')),
    path('permission/', include('authentication.urls.permission_urls')),
    path('role/', include('authentication.urls.role_urls')),
    path('designation/', include('authentication.urls.designation_urls')),

    path('country/', include('authentication.urls.country_urls')),
    path('branch/', include('authentication.urls.branch_urls')),
    path('city/', include('authentication.urls.city_urls')),

    path('receipt/', include('receipts.urls')),
    path('report/', include('reports.urls')),
    

	# YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('djoser/auth/', include('djoser.urls')),
    path('djoser/auth/', include('djoser.urls.jwt')),

	re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
