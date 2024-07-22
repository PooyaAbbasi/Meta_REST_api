from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from BookListAPI.views import *

app_name = 'book_list_api'

urlpatterns = [
    # path('books', list_books, name='list_books'),
    path('books', BookListView.list_books, name='list_books'),
    path('books/<int:pk>', BookDetailView.book_details, name='books-retrieve'),
    # path('categories', CategoryView.list_categories, name='list_categories'),
    # path('categories/create', CategoryView.category_create, name='category_create'),
    # path('categories/<int:pk>', CategoryView.category_details, name='categories-retrieve'),
    path('categories', CategoryView.as_view(), name='list_categories'),
    path('categories/<int:pk>', CategoryView.as_view(), name='retrieve_category'),

]

# simple_router = SimpleRouter(trailing_slash=False)
# simple_router.register('books', BookView, basename='book')
# urlpatterns += simple_router.urls

# default_router = DefaultRouter(trailing_slash=False)
# default_router.register('books', BookView)
# default_router.register('borrow/book', BorrowBookView, basename='borrow_book')
# urlpatterns += default_router.urls
