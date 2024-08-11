from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import *


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['title', 'slug', 'menu_items']
        extra_kwargs = {
            'slug': {'read_only': True}
        }

    menu_items = serializers.SlugRelatedField(slug_field='title', read_only=True, many=True)


class MenuItemSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(slug_field='title', queryset=Category.objects.all(), required=False)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'featured', 'price', 'category', 'link_item']
        extra_kwargs = {
            'featured': {'required': True},
        }

    link_item = serializers.SerializerMethodField(method_name='get_link', read_only=True)

    def get_link(self, menuitem_obj: MenuItem):
        return menuitem_obj.get_absolute_url()


class CartSerializer(serializers.ModelSerializer):

    menu_item = MenuItemSerializer()
    user = serializers.SlugRelatedField(slug_field='username',
                                        queryset=User.objects.all(),
                                        default=serializers.CurrentUserDefault())

    class Meta:
        model = Cart
        fields = ['user', 'menu_item', 'quantity', 'unit_price', 'price']
        validators = (
            UniqueTogetherValidator(fields=('user', 'menu_item'), queryset=Cart.objects.all()),
        )
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    user_full_name = serializers.SerializerMethodField(read_only=True)
    time_ordered = serializers.DateTimeField(source='date_time', read_only=True)
    items = serializers.RelatedField(many=True, queryset=OrderItem.objects.all())

    delivery_crew_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'user', 'user_full_name', 'total_price',
            'delivery_crew', 'time_ordered', 'status', 'items',
            'delivery_crew_name'
        ]
        extra_kwargs = {
            'status': {'help_text': 'is delivered or not'},
            'delivery_crew': {'write_only': True},
        }

    def get_user_full_name(self, order: Order):
        return f'{order.user.first_name} {order.user.last_name}'

    def get_delivery_crew_name(self, order: Order):
        return f'{order.delivery_crew.first_name} {order.delivery_crew.last_name}'


class OrderItemSerializer(serializers.ModelSerializer):

    menu_item = MenuItemSerializer(read_only=True)
    order = serializers.HyperlinkedRelatedField(view_name='order-detail', read_only=True)
    # Todo view name for order details
    menu_item_link = serializers.SerializerMethodField(method_name='get_menu_item_link')

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'unit_price', 'quantity',]
        validators = (
            UniqueTogetherValidator(fields=('menu_item', 'order'), queryset=OrderItem.objects.all()),
        )
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
        read_only_fields = ['menu_item', 'unit_price', 'quantity']

    def get_menu_item_link(self, this_order_item: OrderItem):
        """
        :param this_order_item:
        :return:absolute url for menu item
        """
        return this_order_item.menu_item.get_absolute_url()

