from typing import Union

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.request import Request as BaseRequests, HttpRequest
from rest_framework.response import Response

from api.filters import NameSearchFilter
from api.pagination import DefaultPagination
from api.permissions import RecipePermission
from .models import Ingredient, Recipe, Favorite, ShoppingCart
from .serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    FavoriteSerializer, ShoppingCartSerializer)
from .filters import RecipeFilter
from .utils import get_csv_data


User = get_user_model()
Request = Union[BaseRequests, HttpRequest]


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related('recipe_ingredients')
    serializer_class = RecipeWriteSerializer
    pagination_class = DefaultPagination
    permission_classes = (RecipePermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer: RecipeWriteSerializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'], detail=True,
        url_path='favorite', permission_classes=[IsAuthenticated]
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
        delete_data = favorite_objs.delete()
        if delete_data[0] == 0:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': 'Рецепта нет в избранном'},
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        delete_data = shopping_card_objs.delete()
        if delete_data[0] == 0:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': 'Рецепта нет в корзине'},
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'], detail=False,
        url_path='download_shopping_cart'
    )
    def download_shopping_card(self, request: Request):
        user = request.user
        ingredients = ShoppingCart.objects.values(
            'recipe__recipe_ingredients__ingredient__name',
            'recipe__recipe_ingredients__ingredient__measurement_unit'
        ).filter(user=user).annotate(
            amount=Sum('recipe__recipe_ingredients__amount'))
        data = get_csv_data(ingredients)
        return FileResponse(
            data,
            as_attachment=True,
            filename='shopping_list',
            content_type='text/csv',
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request: Request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/s/{recipe.pk}')
        return Response(
            data={'short-link': short_link},
            status=status.HTTP_200_OK
        )
