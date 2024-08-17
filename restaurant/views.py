from typing import *

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404


from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings


from restaurant.models import *
from restaurant.serializers import *
from restaurant.permissions import *
from restaurant.serializers import validate_two_decimal_places
# Create your views here.


def _get_user_group_names(user: User) -> List[str]:
    """
    :returns: List of names of all groups of given user object.
    """
    return [group.name for group in user.groups.all()]


class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request.user.group_names = _get_user_group_names(request.user)
        return request

    authentication_classes = (TokenAuthentication, )

    def get_permissions(self):
        manager_actions = ['list', 'retrieve', 'update', 'partial_update', 'destroy', 'create', 'options']
        costumer_actions = ['list', 'retrieve',]
        delivery_crew_actions = ['list', 'retrieve',]
        restaurant_permission = RestaurantPermission(self.request.user,
                                                     manager_actions,
                                                     delivery_crew_actions,
                                                     costumer_actions)
        return restaurant_permission


class GroupManegerViewSet(ViewSet):

    # permission_classes = [IsManager,]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = UserSerializer

    def list(self, request: Request, group_name: str) -> Response:
        """
        :return: Paginated Response object containing a list of users of provided group name.
                with status code 200.
        """
        group_name = GroupManegerViewSet.get_lookup_group_name(raw_group_name=group_name)
        users = get_object_or_404(Group, name=group_name).user_set.all()
        return self.get_paginated_response(query_set=users, request=request)

    def create(self, request: Request, group_name: str) -> Response:
        """
        Adds the group with group_name to user groups with username wich is contained in request.data .
        :return: Response 201 created or 400 bad request if username field is not provided in request.data .
        """

        if username := request.data.get('username'):
            group_name = GroupManegerViewSet.get_lookup_group_name(raw_group_name=group_name)

            group = get_object_or_404(Group, name=group_name)
            user = get_object_or_404(User, username=username)
            user.groups.add(group)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            data = {'message': 'username: [this field is required]'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, group_name: str, username: str) -> Response:
        """ Removes the group with group_name from user groups.
        :return: Response 200 OK.
        """
        group_name = GroupManegerViewSet.get_lookup_group_name(raw_group_name=group_name)
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name=group_name)
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)

    @classmethod
    def get_lookup_group_name(cls, raw_group_name: str) -> str:
        """ :return: Appropriate group name to lookup in database."""
        return raw_group_name.replace('-', '_')

    def get_paginated_response(self, query_set: QuerySet, request: Request) -> Response:
        paginator: PageNumberPagination = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(query_set, request)
        serializer = self.serializer_class(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)


class CartViewSet(ViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request: Request) -> Response:
        serializer = self.serializer_class(self.get_list_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def add(self, request: Request) -> Response:
        new_cart = self.serializer_class(data=request.data, context={'request': request})
        new_cart.is_valid(raise_exception=True)
        new_cart.save()
        return Response(new_cart.data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, menuitem_id) -> Response:
        get_object_or_404(Cart, menu_item=menuitem_id, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def clear_carts(self, request: Request) -> Response:
        carts = self.get_carts_of_user()
        for cart in carts.all():
            cart.delete()
        return Response(status=status.HTTP_200_OK)

    def get_carts_of_user(self) -> QuerySet:
        return self.request.user.cart_set

    def get_list_queryset(self):
        carts = self.get_carts_of_user()
        return carts.prefetch_related('menu_item__category').all()


class OrderViewSet(GenericViewSet):
    serializer_class = OrderSerializer
    lookup_url_kwarg = 'id'

    def initialize_request(self, request, *args, **kwargs):
        request = request = super().initialize_request(request, *args, **kwargs)
        request.user.group_names = _get_user_group_names(request.user)
        return request

    def list(self, request: Request) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, id: int) -> Response:
        order = self.get_object()
        serializer = self.serializer_class(order, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, id: int):
        order = self.get_object()
        new_status: bool = request.data.get('status')
        partial_data = {'status': new_status}
        serializer = self.serializer_class(instance=order,
                                           data=partial_data,
                                           partial=True,
                                           context=self.get_serializer_context())

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: Request, id: int) -> Response:
        order = self.get_object()
        print(request.data.__repr__())
        serializer = self.serializer_class(instance=order,
                                           data=self.request.data,
                                           partial=True,
                                           context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, id: int):
        order = self.get_object()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        user = self.request.user
        order_id = self.kwargs.get(self.lookup_url_kwarg)
        queryset = Order.objects.select_related('user', 'delivery_crew').prefetch_related('order_items__menu_item')
        if RestaurantPermission.is_manager(user.group_names):
            return get_object_or_404(queryset, pk=order_id)
        elif RestaurantPermission.is_delivery_crew(user.group_names):
            order = get_object_or_404(queryset, delivery_crew=user, pk=order_id)
            return order
        else:
            order = get_object_or_404(queryset, user=user, pk=order_id)
            return order

    def create(self, request: Request) -> Response:
        carts: QuerySet = self.request.user.cart_set.all()

        if not carts.exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'No carts exists.'})

        new_order_obj = self._create_new_order(carts)
        self._create_order_items(carts, new_order_obj)
        self._delete_all_carts(carts)
        # updated_order_serializer = self._update_order_again(new_order_obj)
        return Response(status=status.HTTP_201_CREATED)

    def _create_new_order(self, carts: QuerySet) -> Order:
        """ create a new order instance for this authenticated user and save it.
        :return: created order instance.
        """
        new_order_data = {
            'total_price': Cart.get_total_price_for_carts(carts)
        }
        serializer = self.serializer_class(data=new_order_data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def _get_total_price_of(self, carts: QuerySet) -> Decimal:
        return Cart.get_total_price_for_carts(carts)

    def _create_order_items(self, carts: QuerySet, order: Order):
        """ create order items based on the cart items of authenticated user related to order."""
        for cart in carts:
            obj = OrderItem.objects.create(order=order,
                                           menu_item=cart.menu_item,
                                           quantity=cart.quantity,
                                           unit_price=cart.unit_price)

    def _delete_all_carts(self, carts: QuerySet):
        """ delete all carts of authenticated user."""
        for cart in carts:
            cart.delete()

    def _update_order_again(self, order: Order) -> OrderSerializer:
        """ to assign the value of total_price for the order"""
        order_update_serializer = self.serializer_class(instance=order)
        order_update_serializer.is_valid(raise_exception=True)
        return order_update_serializer

    def get_permissions(self):
        """
        :return: related permissions for specified actions
        """
        manager_actions = ['destroy', 'list', 'retrieve', 'update', 'create', 'partial_update']
        delivery_crew_actions = ['partial_update', 'list']
        costumer_actions = ['create', 'retrieve', 'list']
        group_names_of_user = self.request.user.group_names
        restaurant_permission = RestaurantPermission(group_names_of_user,
                                                     manager_actions,
                                                     delivery_crew_actions
                                                     , costumer_actions)

        return [restaurant_permission, ]

    def get_queryset(self):
        """
        :returns: if user is delivery crew, assigned_orders.
                if user is manager, all order objects.
                if user is costumer, all user orders.
        """
        user = self.request.user
        if RestaurantPermission.is_manager(user.group_names):
            return (Order.objects.all()
                    .select_related('user', 'delivery_crew')
                    .prefetch_related('order_items__menu_item')
                    )
        elif RestaurantPermission.is_delivery_crew(user.group_names):
            return (user.assigned_orders.all()
                    .select_related('user', 'delivery_crew')
                    .prefetch_related('order_items__menu_item')
                    )
        else:
            return (user.orders.all()
                    .select_related('user', 'delivery_crew')
                    .prefetch_related('order_items__menu_item')
                    )
