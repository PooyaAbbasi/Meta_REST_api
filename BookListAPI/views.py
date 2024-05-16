from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view, action
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Book
from BookListAPI import serializers

from django.shortcuts import get_object_or_404
# Create your views here.


@api_view(['GET', 'POST'])
def list_books(request):
    return Response(data='List of Books', status=status.HTTP_200_OK)


class BookListView:

    @staticmethod
    @api_view()
    def list_books(request):
        books = Book.objects.all()
        serialized_data = serializers.BookCustomSerializer(books, many=True)

        return Response(data=serialized_data.data, status=status.HTTP_200_OK)


class BookDetailView:
    @staticmethod
    @api_view()
    def book_details(request, pk):
        book = get_object_or_404(Book, pk=pk)
        serialized_item = serializers.BookCustomSerializer(book)
        return Response(data=serialized_item.data)


class BookView(ViewSet):

    def retrieve(self, request, pk=None):
        return Response(f'get book : {pk}', status=status.HTTP_200_OK)

    def list(self, request):
        return Response(data='list of books in list view set ', status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        return Response(f'destroy book : {pk}', status=status.HTTP_200_OK)


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


class BookRetrieveView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer
