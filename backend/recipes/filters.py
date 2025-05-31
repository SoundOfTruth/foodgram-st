from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_favorites',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_carts',
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_favorites(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=user)
            return queryset.exclude(favorites__user=user)
        return queryset

    def filter_shopping_carts(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_carts__user=user)
            return queryset.exclude(shopping_carts__user=user)
        return queryset
