from rest_framework import serializers
from BookListAPI.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['title', 'author']
