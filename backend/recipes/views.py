import io
import csv
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.request import Request as BaseRequests, HttpRequest
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from typing import Union


from .models import Ingredient, Recipe, Favorite, ShoppingCart
from .serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    FavoriteSerializer, ShoppingCartSerializer)
from .permissions import RecipePermission
from .filters import NameSearchFilter
from api.pagination import DefaultPagination


User = get_user_model()
Request = Union[BaseRequests, HttpRequest]


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related('ingredients')
    serializer_class = RecipeWriteSerializer
    pagination_class = DefaultPagination
    permission_classes = (RecipePermission, )
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('author',)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart')
            if is_favorited:
                queryset = (
                    queryset.filter(favorite__user=user)
                    if is_favorited == '1'
                    else queryset.exclude(favorite__user=user)
                )
            if is_in_shopping_cart:
                queryset = (
                    queryset.filter(in_shopping_cart__user=user)
                    if is_in_shopping_cart == '1'
                    else queryset.exclude(in_shopping_cart__user=user)
                )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer: RecipeWriteSerializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'], detail=True,
        url_path="favorite", permission_classes=[IsAuthenticated]
    )
    def favorite(self, request: Request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            data = {'user': request.user.pk, 'recipe': recipe.pk}
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                serializer.to_representation(instance),
                status=status.HTTP_201_CREATED,
            )
        favorite_objs = Favorite.objects.filter(
            user=request.user, recipe=recipe)
        if favorite_objs.exists():
            favorite_objs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': 'Рецепта нет в избранном'},
        )

    @action(
        methods=['POST', 'DELETE'], detail=True,
        url_path='shopping_cart',
    )
    def shopping_card(self, request: Request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            data = {'user': request.user.pk, 'recipe': recipe.pk}
            serializer = ShoppingCartSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                serializer.to_representation(instance),
                status=status.HTTP_201_CREATED,
            )
        shopping_card_objs = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if shopping_card_objs.exists():
            shopping_card_objs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': 'Рецепта нет в избранном'},
        )

    @action(
        methods=['GET'], detail=False,
        url_path='download_shopping_cart'
    )
    def download_shopping_card(self, request: Request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if not shopping_cart.exists():
            return Response(
                {"error": "Корзина покупок пуста."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ingredients = shopping_cart.values(
            'recipe__ingredients__ingredient__name',
            'recipe__ingredients__ingredient__measurement_unit'
        ).annotate(amount=Sum('recipe__ingredients__amount'))
        stream = io.StringIO()
        writer = csv.writer(stream)
        for ingredient in ingredients:
            name = ingredient['recipe__ingredients__ingredient__name']
            measurement_unit = ingredient[
                'recipe__ingredients__ingredient__measurement_unit']
            amount = ingredient['amount']
            payload = [f'{name} ({measurement_unit})', amount]
            writer.writerow(payload)
        return FileResponse(
            stream.getvalue(),
            as_attachment=True,
            filename="shopping_list",
            content_type="text/csv",
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request: Request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = f'localhost/s/{recipe.pk}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
