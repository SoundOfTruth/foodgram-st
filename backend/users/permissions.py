from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.request import Request as DrfRequest
from typing import Union


from .models import CustomUser


Request = Union[HttpRequest, DrfRequest]


class UserPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request: Request, view, obj: CustomUser):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_anonymous:
            return False
        return (
            obj.pk == request.user.pk
            or request.user.is_superuser
            or request.user.is_staff
        )
