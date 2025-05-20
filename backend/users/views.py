from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request as BaseRequests, HttpRequest
from rest_framework.response import Response
from typing import Union


from api.pagination import DefaultPagination
from .subscription_serializer import (
    SubscriptionSerializer)
from .serializers import CustomUserSerializer, AvatarSerializer
from .models import CustomUser, Subscription
from .permissions import UserPermission


Request = Union[BaseRequests, HttpRequest]


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (UserPermission,)
    pagination_class = DefaultPagination

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            context={'request': self.request},
            *args, **kwargs
        )

    @action(
        methods=['PUT', 'DELETE'], detail=False,
        url_path="me/avatar", permission_classes=[IsAuthenticated]
    )
    def change_avatar(self, request: Request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        if self.request.method == 'PUT':
            if serializer.is_valid(raise_exception=True):
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
            serializer = SubscriptionSerializer(
                data={'user': user.pk, 'author': author.pk},
                context=context
            )
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                return Response(
                    status=status.HTTP_201_CREATED,
                    data=serializer.to_representation(instance))
        subscription = Subscription.objects.filter(
            user=user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data='subscription not exists'
        )

    @action(
        methods=['GET'], detail=False,
        url_path='subscriptions', permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request: Request):
        subs = self.request.user.subscriptions.all()
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(subs, request)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
