from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from BookListAPI.views import *

app_name = 'book-list-api'

urlpatterns = [
    path('book', BookCreatView.as_view(), name='book-create'),
    path('books', BookListView.list_books, name='list-books'),
    path('books/<int:pk>', book_detail, name='book-detail'),
    # path('categories', CategoryView.list_categories, name='list_categories'),
    # path('categories/create', CategoryView.category_create, name='category_create'),
    # path('categories/<int:pk>', CategoryView.category_details, name='categories-retrieve'),
    path('categories', CategoryView.as_view(), name='list-categories'),
    path('categories/<int:pk>', CategoryView.as_view(), name='detail-category'),

    #  authentication implementation
    path('secret', secret_message, name='secret'),
    path('api-token-auth', obtain_auth_token, name='obtain-auth-token'),

    # Rate_limit
    path('throttle-check', throttle_check, name='throttle-check'),
    path('users/manage/groups', add_group, name='add-group'),

]

# simple_router = SimpleRouter(trailing_slash=False)
# simple_router.register('books', BookView, basename='book')
# urlpatterns += simple_router.urls

default_router = DefaultRouter(trailing_slash=False)
default_router.register('books-set', BookViewSet, basename='book')
# default_router.register('borrow/book', BorrowBookView, basename='borrow_book')
urlpatterns += default_router.urls


