from rest_framework import permissions
# from django.contrib.auth.models import Group, User


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.groups.filter(name='manager').exists()) and request.user.is_authenticated


class IsDeliveryCrew(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.groups.filter(name='delivery_crew').exists()) and request.user.is_authenticated
