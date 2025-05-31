from typing import Union

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request as BaseRequests, HttpRequest
from rest_framework.response import Response

from api.pagination import DefaultPagination
from .models import CustomUser, Subscription
from .serializers import CustomUserSerializer, AvatarSerializer
from .subscription_serializer import (
    CreateSubscriptionSerializer,
    SubscriptionSerializer
)


Request = Union[BaseRequests, HttpRequest]


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = DefaultPagination

    @action(
        methods=['PUT', 'DELETE'], detail=False,
        url_path="me/avatar", permission_classes=[IsAuthenticated]
    )
    def change_avatar(self, request: Request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        if self.request.method == 'PUT':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                status=status.HTTP_200_OK,
                data=serializer.data
            )
        user.avatar = None
        user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=['POST', 'DELETE'], detail=True,
        url_path='subscribe', permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request: Request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)
        context = {'request': request}
        if self.request.method == 'POST':
            serializer = CreateSubscriptionSerializer(
                data={'user': user.pk, 'author': author.pk},
                context=context
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data=serializer.to_representation(instance))
        subscription = Subscription.objects.filter(
            user=user, author=author)
        deleted_count, _ = subscription.delete()
        if deleted_count == 0:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='Пользователя нет в подписках'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'], detail=False,
        url_path='subscriptions', permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request: Request):
        subs = CustomUser.objects.filter(
            subscribers__user=self.request.user
        )
        page = self.paginate_queryset(subs)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
