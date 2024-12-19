from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import *
from rest_framework import serializers
from decimal import Decimal, ROUND_DOWN
from djoser.serializers import UserSerializer as BaseUserSerializer


def validate_two_decimal_places(value):
    # Ensure the value is a Decimal
    if not isinstance(value, Decimal):
        raise serializers.ValidationError("This field must be a decimal.")

    # Quantize the value to 2 decimal places
    cleaned_value = value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    return cleaned_value


class CustomDecimalField(serializers.DecimalField):

    def to_internal_value(self, data):
        """ converts decimal value to decimal value and removing more than two decimal places.
        :returns: super().to_internal_value(data)
        """
        try:
            data = Decimal(data)
        except (ValueError, TypeError) as e:
            self.fail('invalid', value=data)

        cleaned_data = validate_two_decimal_places(data)
        return super().to_internal_value(cleaned_data)


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class CategorySerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if request and self.context.get('view').action == 'list':
            self.fields.pop('menu_items')

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'menu_items', ]
        extra_kwargs = {
            'slug': {'read_only': True},
            'menu_items': {'read_only': True},
        }

    menu_items = serializers.PrimaryKeyRelatedField(read_only=True, many=True)


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    price = CustomDecimalField(max_digits=10, decimal_places=2)

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
    menu_item_info = serializers.SerializerMethodField(read_only=True)
    user = serializers.SlugRelatedField(slug_field='username',
                                        queryset=User.objects.all(),
                                        default=serializers.CurrentUserDefault())

    menu_item = serializers.PrimaryKeyRelatedField(write_only=True,
                                                   queryset=MenuItem.objects.all(),
                                                   required=True,
                                                   help_text='id of menu-item')

    class Meta:
        model = Cart
        fields = ['user', 'menu_item_info', 'quantity', 'unit_price', 'price', 'menu_item']
        validators = (
            UniqueTogetherValidator(fields=('user', 'menu_item'), queryset=Cart.objects.all()),
        )
        extra_kwargs = {
            'quantity': {'min_value': 1, 'required': True},
        }
        depth = 1

    def get_menu_item_info(self, cart: Cart):
        return MenuItemSerializer(cart.menu_item).data


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    user_full_name = serializers.SerializerMethodField(read_only=True)
    time_ordered = serializers.DateTimeField(source='date_time', read_only=True)
    items = serializers.SerializerMethodField(method_name='get_items', read_only=True)

    delivery_crew_name = serializers.SerializerMethodField(read_only=True)
    delivery_crew = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), required=False)
    total_price = CustomDecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_full_name', 'total_price',
            'delivery_crew', 'time_ordered', 'status', 'items',
            'delivery_crew_name'
        ]
        extra_kwargs = {
            'status': {'help_text': 'is delivered or not', 'default': False},
        }

    def get_user_full_name(self, order: Order):
        return {'username': order.user.username,
                'first_name': order.user.first_name,
                'last_name': order.user.last_name, }

    def get_delivery_crew_name(self, order: Order):
        if order.delivery_crew:
            return {'username': order.delivery_crew.username,
                    'first_name': order.delivery_crew.first_name,
                    'last_name': order.delivery_crew.last_name}
        else:
            return None

    def get_items(self, order: Order):
        return OrderItemSerializer(order.order_items.all(), many=True).data

    def validate_delivery_crew(self, delivery_crew: User):
        if delivery_crew.groups.filter(name='delivery_crew').exists():
            return delivery_crew
        else:
            raise serializers.ValidationError(detail='provided user id does not belong to delivery crew')


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(write_only=True, queryset=MenuItem.objects.all())
    menu_item_link = serializers.SerializerMethodField(method_name='get_menu_item_link')

    order = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'unit_price', 'quantity', 'menu_item_link', 'price', 'order']
        validators = (
            UniqueTogetherValidator(fields=('menu_item', 'order'), queryset=OrderItem.objects.all()),
        )
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
        read_only_fields = ['menu_item_link', 'unit_price', 'price', 'order']

    def get_menu_item_link(self, this_order_item: OrderItem):
        """
        :param this_order_item:
        :return:absolute url for menu item
        """
        return this_order_item.menu_item.get_absolute_url()
