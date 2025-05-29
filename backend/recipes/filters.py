import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.ChoiceFilter(
        choices=[
            ('1', 'True'),
            ('0', 'False'),
        ],
        method='filter_favorites',
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=[
            ('1', 'True'),
            ('0', 'False'),
        ],
        method='filter_shopping_carts',
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_favorites(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                return queryset.filter(favorites__user=user)
            return queryset.exclude(favorites__user=user)
        return queryset

    def filter_shopping_carts(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                return queryset.filter(shopping_carts__user=user)
            return queryset.exclude(shopping_carts__user=user)
        return queryset
