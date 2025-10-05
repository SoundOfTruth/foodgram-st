from typing import Union

from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.request import Request as DrfRequest

from recipes.models import Recipe
from users.models import CustomUser


Request = Union[HttpRequest, DrfRequest]


class RecipePermission(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request: Request, view, obj: Recipe):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class UserPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request: Request, view, obj: CustomUser):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and obj.pk == request.user.pk
        )
