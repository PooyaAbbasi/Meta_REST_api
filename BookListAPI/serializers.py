from rest_framework import serializers
from BookListAPI.models import Book


class BookSerializer(serializers.ModelSerializer):
    # representing user_name as 'id' attribute of Book instances
    user_name = serializers.IntegerField(source='id', read_only=True)

    # adding a prepared field
    full_author_name = serializers.SerializerMethodField()
    # the associated method might be named like get_{field_name} or should be passed

    class Meta:
        model = Book
        fields = ['user_name', 'title', 'author', 'full_author_name']
        # '__all__' represent all of abow fields.

    def get_full_author_name(self, book: Book) -> str:
        return f'mr or ms {book.author}'


class BookCustomSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    author = serializers.CharField(max_length=100, read_only=True)
