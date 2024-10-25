from rest_framework import permissions
from django.contrib.auth.models import Group, User


class RestaurantPermission(permissions.IsAuthenticated):
    """
        Restaurant permission class is provided customized for Restaurant app
        to reduce queries and other optimizations and less code
        this class can check permissions based on list of actions that provided for each group
        (current groups : delivery_crew, manager and customers contains ordinary users).

        This permission class has classmethods to check user is belonged to target group or not.
    """

    def __init__(self, user_group_names: list[str],
                 manager_permitted_actions: list[str],
                 delivery_crew_permitted_actions: list[str],
                 costumer_permitted_actions: list[str],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_group_names = user_group_names
        self.delivery_crew_permitted_actions = delivery_crew_permitted_actions
        self.manager_permitted_actions = manager_permitted_actions
        self.costumer_permitted_actions = costumer_permitted_actions

    def has_permission(self, request, view):
        super_permission = super().has_permission(request, view)
        cls = self.__class__

        if cls.is_manager(self.user_group_names):
            # manager has full access to all types of actions
            return (view.action in self.manager_permitted_actions) and super_permission

        elif cls.is_delivery_crew(self.user_group_names):
            return (view.action in self.delivery_crew_permitted_actions) and super_permission

        else:
            return (view.action in self.costumer_permitted_actions) and super_permission

    @classmethod
    def is_manager(cls, user_group_names: list[str]) -> bool:
        return 'manager' in user_group_names

    @classmethod
    def is_delivery_crew(cls, user_group_names: list[str]) -> bool:
        return 'delivery_crew' in user_group_names

    @classmethod
    def is_costumer(cls, user_group_names: list[str]) -> bool:
        return not (cls.is_manager(user_group_names) or cls.is_delivery_crew(user_group_names))
