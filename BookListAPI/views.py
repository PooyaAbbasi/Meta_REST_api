from django.db.models import QuerySet
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, action, renderer_classes
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from BookListAPI import serializers
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.request import Request
from django.core.paginator import Paginator, EmptyPage, Page

from django.shortcuts import get_object_or_404

from .serializers import BookSerializer
from .models import Book, Category

# Create your views here.


"""
@api_view(['GET', 'POST'])
def list_books(request):
    return Response(data='List of Books', status=status.HTTP_200_OK)
"""


class BookListView:

    @staticmethod
    @api_view(['GET',])
    @renderer_classes((TemplateHTMLRenderer, CSVRenderer, JSONRenderer))
    def list_books(request):

        books = BookListView.get_queryset(request)
        books = BookListView.get_paginated_items(request, books)
        serializer = serializers.BookSerializer(books, many=True, context={'request': request})

        if request.GET['format'] == 'html':
            welcome_message = 'welcome to list of books'
            return Response(
                {'data': serializer.data, 'welcome_message': welcome_message},
                template_name='BookListAPI/book-items.html',
            )

        if request.GET['format'] == 'csv':
            return Response(data=serializer.data, content_type='text/csv')

        if request.GET['format'] == 'json':
            return Response(data=serializer.data, content_type='application/json')

    @staticmethod
    def get_queryset(request: Request) -> QuerySet:
        items = Book.objects.select_related('category').all()

        query_params = request.query_params.dict()

        if target_category := query_params.get('category'):
            items = items.filter(category__name=target_category)

        if search := query_params.get('search'):
            items = items.filter(title__icontains=search)

        if ordering_fields := query_params.get('ordering'):
            ordering_fields = ordering_fields.split(',')
            items = items.order_by(*ordering_fields)

        return items
        pass

    @staticmethod
    def get_paginated_items(request: Request, queryset: QuerySet):
        per_page = request.query_params.get('per-page', default=3)
        page_no = request.query_params.get('page', default=1)
        paginator = Paginator(queryset, per_page)
        try:
            return paginator.page(page_no)
        except EmptyPage:
            return []


@api_view(['GET', 'PATCH'])
def book_detail(request, pk):

    if request.method == 'GET':
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book, context={'request': request})
        return Response(data=serializer.data, )

    if request.method == 'PATCH':
        book = get_object_or_404(Book, pk=pk)

        serializer = BookSerializer(instance=book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView:
    @staticmethod
    @api_view()
    def book_details(request, pk):
        book = get_object_or_404(Book, pk=pk)
        serialized_item = serializers.BookSerializer(book, context={'request': request})
        return Response(data=serialized_item.data)


class CategoryView(APIView):

    def get(self, request, pk=None):

        if pk:
            category = get_object_or_404(Category, pk=pk)
            serializer = serializers.CategorySerializer(category)
        else:
            category = Category.objects.prefetch_related('books').all()
            serializer = serializers.CategorySerializer(category, many=True)

        return Response(data=serializer.data)
        pass

    def post(self, request):
        new_category = serializers.CategorySerializer(data=request.data)
        if new_category.is_valid():
            new_category.save()
            return Response(data=new_category.data, status=status.HTTP_201_CREATED)

        return Response(new_category.errors, status.HTTP_402_PAYMENT_REQUIRED)


class BookViewSet(ModelViewSet):
    queryset = Book.objects.select_related('category').all()
    ModelViewSet.renderer_classes = [TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer]
    serializer_class = BookSerializer

    def get_template_names(self):
        if self.action == 'list':
            return ('BookListAPI/book-items.html', )
        else:
            return ()

    def list(self, request, *args, **kwargs):
        response = super(BookViewSet, self).list(request, *args, **kwargs)

        if self.request.query_params.get('format') == 'html':
            response.data = {'data': response.data}

        return response

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ['title', 'author', 'category__name']
    search_fields = ['title', 'author', 'category__name']  # will be searched in all fields ignore case
    search_query_param = 'find'


class BookCollectionView(APIView):
    def get(self, request):
        books = Book.objects.all()
        return Response(data=books, status=status.HTTP_200_OK)
        pass

    def post(self, request):
        author = request.data.get('author')
        return Response(data=author, status=status.HTTP_200_OK)


class BorrowBookView(RetrieveAPIView):

    queryset = Book.objects.all()
    """ permission_classes = [IsAuthenticated, IsAdminUser]
    """
    serializer_class = serializers.BookSerializer

    # customizing permissions and selected authentication
    def get_permissions(self):
        permission_classes = []
        if self.request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            permission_classes.append(IsAuthenticated)

        return [permission() for permission in permission_classes]

    # customizing queryset
    def get_queryset(self):
        return Book.objects.filter(author=self.request.user)

    # customizing CRUD methods
    # other methods are post(), put(), patch()
    def get(self, request, pk, *args, **kwargs):
        return Response(f"Book Not Found {pk}", status=status.HTTP_404_NOT_FOUND)


class BookCreatView(CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer


class SingleBookView(RetrieveUpdateAPIView, DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer
