"""
URL configuration for BookList project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, URLPattern
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('BookListAPI.urls'),),
    path('api/v1/', include('restaurant.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    # Djoser urls
    path('api/v1/', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('auth/jwt-token/obtain', TokenObtainPairView.as_view(), name='token_jwt_obtain'),
    path('auth/jwt-token/refresh', TokenRefreshView.as_view(), name='token_jwt_refresh'),
    path('auth/jwt-token/blacklist', TokenBlacklistView.as_view(), name='token_jwt_blacklist'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)