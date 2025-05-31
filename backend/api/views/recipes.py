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
from rest_framework.filters import OrderingFilter

from api.filters import NameSearchFilter, RecipeFilter
from api.pagination import DefaultPagination
from api.permissions import RecipePermission
from api.serializers.recipes import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart
)
from recipes.utils import get_csv_data


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
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer: RecipeWriteSerializer):
        serializer.save(author=self.request.user)

    def create_delete_recipe_relation(self, object, serializer, pk, error):
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            data = {'user': self.request.user.pk, 'recipe': recipe.pk}
            serializer = serializer(
                data=data,
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                serializer.to_representation(instance),
                status=status.HTTP_201_CREATED,
            )
        favorite_objs = object.objects.filter(
            user=self.request.user, recipe=recipe
        )
        deleted_count, _ = favorite_objs.delete()
        if deleted_count == 0:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': error},
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'], detail=True,
        url_path='favorite', permission_classes=[IsAuthenticated]
    )
    def favorite(self, request: Request, pk=None):
        return self.create_delete_recipe_relation(
            object=Favorite,
            serializer=FavoriteSerializer,
            pk=pk,
            error='Рецепта нет в избранном'
        )

    @action(
        methods=['POST', 'DELETE'], detail=True,
        url_path='shopping_cart',
    )
    def shopping_card(self, request: Request, pk=None):
        return self.create_delete_recipe_relation(
            object=ShoppingCart,
            serializer=ShoppingCartSerializer,
            pk=pk,
            error='Рецепта нет в корзине'
        )

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
