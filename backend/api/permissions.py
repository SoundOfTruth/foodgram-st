from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.request import Request as DrfRequest
from typing import Union


Request = Union[HttpRequest, DrfRequest]


class DefaultPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request: Request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_superuser
            or request.user.is_superuser
        )
