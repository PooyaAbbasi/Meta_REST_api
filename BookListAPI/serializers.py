from rest_framework import serializers
from BookListAPI.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['title', 'author']


class BookCustomSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    author = serializers.CharField(max_length=100, read_only=True)
