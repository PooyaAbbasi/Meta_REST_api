from django.urls import path
from rest_framework.routers import DefaultRouter
from restaurant import views


app_name = 'restaurant'

urlpatterns = [
    path('menu-items/<slug:slug>/<int:pk>',
         views.MenuItemViewSet.as_view({'get': 'retrieve'}),
         name='menu-item-detail'),

]

default_router = DefaultRouter(trailing_slash=False)
default_router.register('menu-items', views.MenuItemViewSet, basename='menu-items',)

urlpatterns += default_router.urls
