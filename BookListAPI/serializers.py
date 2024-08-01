import bleach
from rest_framework import serializers
from rest_framework.fields import UUIDField

from BookListAPI.models import Book, Category
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from io import BytesIO


class CategorySerializer(serializers.ModelSerializer):
    books = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['name', 'books']


class BookSerializer(serializers.ModelSerializer):
    # representing user_name as 'id' attribute of Book instances
    # user_name = serializers.IntegerField(source='id')

    # adding a prepared field
    full_author_name = serializers.SerializerMethodField(read_only=True)
    # the associated method might be named like get_{field_name} or should be passed

    ''' ####################### '''
    ''' Types of Related Fields or Extending HyperLinkedModelSerializer '''

    # category = CategorySerializer(read_only=True)

    # category = serializers.PrimaryKeyRelatedField(read_only=True)

    # category = serializers.StringRelatedField(read_only=True)

    # category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    """ HyperLinkRelatedField 
     Note: view_name is essential and Must be mapped to a url pattern name. (with appname if it is provided)
    """
    # category = serializers.HyperlinkedRelatedField(read_only=True, view_name='book-list-api:detail-category', lookup_field='pk')

    category_id = serializers.IntegerField(write_only=True)
    '''
    all these parameters can be passed by extra_kwargs in Meta class
    price = serializers.DecimalField(source='price', min_value=20, max_digits=10, decimal_places=2)
    '''

    class Meta:
        model = Book
        fields = ['user_name', 'title', 'author', 'full_author_name', 'category', 'category_id', 'price']
        # '__all__' represent all of abow fields.
        depth = 1
        extra_kwargs = {
            'user_name': {'source': 'id', 'read_only': True},
            'price': {'min_value': 20,}
        }

    def get_full_author_name(self, book: Book) -> str:
        return f'mr or ms {book.author}'

    def validate(self, attrs):

        attrs['title'] = bleach.clean(attrs['title'])
        attrs['author'] = bleach.clean(attrs['author'])

        return super().validate(attrs)


class BookCustomSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    author = serializers.CharField(max_length=100, read_only=True)
