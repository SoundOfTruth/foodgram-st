from rest_framework import serializers


from api.fields import Base64ImageField
from users.serializers import CustomUserSerializer
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart
)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = (
            'id', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.shopping_carts.filter(user=request.user).exists()
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time')
        model = Recipe

    def __save_ingredients(self, recipe, ingredients_data):
        recipeingredient_list = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipeingredient_list)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Список ингредиентов не может быть пустым'}
            )
        ingredients_id_set = set(
            ingredient.get('id') for ingredient in ingredients)
        if len(ingredients_id_set) != len(ingredients):
            raise serializers.ValidationError(
                {'ingredients': 'id ингрединтов дублируются'}
            )
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                error = f'Ингредиент с id: {ingredient_id} не существует'
                raise serializers.ValidationError(
                    {'ingredients': error}
                )
        return super().validate(data)

    def create(self, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data
        )
        self.__save_ingredients(recipe, ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('ingredients', None)
        recipe = super().update(instance, validated_data)
        recipe.recipe_ingredients.all().delete()
        self.__save_ingredients(recipe, ingredients_data)
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = SimpleRecipeSerializer(recipe)
        return serializer.to_representation(recipe)


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = SimpleRecipeSerializer(recipe)
        return serializer.to_representation(recipe)
