from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
from django.http import HttpResponse

# Create your views here.


@api_view(['GET', 'POST'])
def list_books(request):
    return Response(data='List of Books', status=status.HTTP_200_OK)


class BookListView:

    @staticmethod
    @api_view()
    def list_books(request):
        return Response(data='list of books Class method ', status=status.HTTP_200_OK)


class Book(ViewSet):

    def get(self, request, pk=None):
        return Response(f'get book : {pk}', status=status.HTTP_200_OK)

    def list(self, request):
        return Response(data='list of books in list view set ', status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        return Response(f'destroy book : {pk}', status=status.HTTP_200_OK)



