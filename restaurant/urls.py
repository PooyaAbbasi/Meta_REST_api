from django.urls import path
from rest_framework.routers import DefaultRouter
from restaurant.views import *

app_name = 'restaurant'

urlpatterns = [
    path('menu-items/<slug:slug>/<int:pk>',
         MenuItemViewSet.as_view({'get': 'retrieve'}),
         name='menu-item-detail'),

    # Group management urls
    path('groups/<str:group_name>/users',
         GroupManegerViewSet.as_view(
             {'get': 'list',
              'post': 'create', }
         ),
         name='group-users-create-or-list'
         ),
    path('groups/<str:group_name>/users/<str:username>',
         GroupManegerViewSet.as_view(
             {'delete': 'destroy'}
         ),
         name='group-users-delete'
         ),

    # cart management urls
    path('cart/menu-items',
         CartViewSet.as_view(
             {
                 'get': 'list',
                 'post': 'add',
                 'delete': 'clear_carts'
             }
         ),
         name='cart-items'
         ),

    path('cart/menu-items/<int:menuitem_id>',
         CartViewSet.as_view(
             {
                 'delete': 'destroy',
             }
         ),
         name='cart-item-destroy'
         ),

]

default_router = DefaultRouter(trailing_slash=False)
default_router.register('menu-items', MenuItemViewSet, basename='menu-items', )
default_router.register('orders', OrderViewSet, basename='orders', )
urlpatterns += default_router.urls
