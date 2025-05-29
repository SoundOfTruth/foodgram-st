from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.request import Request as DrfRequest
from typing import Union


Request = Union[HttpRequest, DrfRequest]


class DefaultPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request: Request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
