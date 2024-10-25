from django.db.models import QuerySet, Avg
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, action, renderer_classes, permission_classes, throttle_classes
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from BookListAPI import serializers
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.request import Request
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from django.core.paginator import Paginator, EmptyPage, Page
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpRequest

from .serializers import BookSerializer
from .models import *
from .throttles import TenUserRateThrottle
# Create your views here.


"""
@api_view(['GET', 'POST'])
def list_books(request):
    return Response(data='List of Books', status=status.HTTP_200_OK)
"""


class BookListView:
    """
        Implementing a class_based view for listing books.
        implementing search and filtering manually.
    """
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
        items = Book.objects.select_related('category').all().annotate(avg_rating=Avg('book_ratings__rating')).order_by('-avg_rating')

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
        """
        :return: paginated queryset of books using Django Paginator
        """
        per_page = request.query_params.get('per-page', default=3)
        page_no = request.query_params.get('page', default=1)
        paginator = Paginator(queryset, per_page)
        try:
            return paginator.page(page_no)
        except EmptyPage:
            return []


@api_view(['GET', 'PATCH'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def book_detail(request, pk):
    """ sample usage of functional view to retrieve book details with limited methods"""

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
    """
    sample usage of decorators in class based view
    """
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
    queryset = Book.objects.select_related('category').all().annotate(avg_rating=Avg('book_ratings__rating'))
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer, TemplateHTMLRenderer]
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_template_names(self):
        if self.action == 'list':
            return ('BookListAPI/book-items.html', )
        else:
            return ()

    def list(self, request: Request, *args, **kwargs):
        response = super(BookViewSet, self).list(request, *args, **kwargs)
        print(f'{request.user.is_authenticated  = }')
        if self.request.query_params.get('format') == 'html':
            response.data = {'data': response.data}

        return response

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ['title', 'author', 'category__name']
    search_fields = ['title', 'author', 'category__name']  # will be searched in all fields ignore case
    search_query_param = 'find'

    # permission_classes = (IsAuthenticatedOrReadOnly, )
    """ conditional permission classes """
    def get_permissions(self):
        perm_classes = []
        if self.action != 'list':
            perm_classes.append(IsAuthenticated)
        return [permissionClass() for permissionClass in perm_classes]

    # throttle_classes = (AnonRateThrottle, TenUserRateThrottle)
    """ conditional throttle classes"""
    def get_throttles(self):
        throttle_classes = []
        if self.action == 'list':
            throttle_classes.append(TenUserRateThrottle)
        else:
            throttle_classes = [UserRateThrottle, AnonRateThrottle]

        return [ThrottleClass() for ThrottleClass in throttle_classes]


class BookCreatView(CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer


class SingleBookView(RetrieveUpdateAPIView, DestroyAPIView):
    """ this view class is sample of using generic views as it is not mapped to any endpoint
    """
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer


@api_view(['GET',])
@permission_classes([IsAuthenticated])
@throttle_classes([TenUserRateThrottle])
def secret_message(request: Request):
    if request.user.groups.filter(name='manager').exists():
        return Response({"secret_message": "The secret of night"})
    else:
        return Response({"secret_message": "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET',])
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({'message': f'successful {request.user.is_anonymous = }'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_group(request: Request):
    username = request.data.get('username')
    group_name = request.data.get('group_name')
    if username and group_name:
        group: Group = get_object_or_404(Group, name=group_name)
        user = get_object_or_404(User, username=username)
        group.user_set.add(user)
        return Response({'message': f'Added {username} to {group_name}'})
    else:
        return Response({'message': 'username and group_name is required'}, status.HTTP_400_BAD_REQUEST)


class RatingView(ListCreateAPIView):
    """

    """

    queryset = Rating.objects.all()
    serializer_class = serializers.RatingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []

        return [IsAuthenticated()]

    throttle_classes = [UserRateThrottle]


def reset_pass_confirm(request, uid, token):
    """
    This is a testing view as a front end application page for getting new password from user
    (Authentication with Djoser)
    """
    return HttpResponse(content='reset your password')

