from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from BookListAPI.views import *

app_name = 'book_list_api'

urlpatterns = [
    # path('books', list_books, name='list_books'),
    # path('books', BookListView.list_books, name='list_books'),
    # path('books/<int=pk>',
    #      Book.as_view(
    #          {
    #              'get': 'get',
    #              'delete': 'destroy'
    #          }
    #      )
    #      ),
    #
    # path('books/<int:pk>', Book.as_view(
    #     {
    #         'get': 'list'
    #     }
    # ))
]

# simple_router = SimpleRouter(trailing_slash=False)
# simple_router.register('books', Book, basename='book')
# urlpatterns += simple_router.urls

default_router = DefaultRouter(trailing_slash=False)
default_router.register('books', Book, basename='book')
urlpatterns += default_router.urls
