from rest_framework import serializers


from api.fields import Base64ImageField
from users.serializers import CustomUserSerializer
from .models import (
    Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        fields = ('ingredient', 'recipe', 'amount')
        model = RecipeIngredient

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount,
        }


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(many=True)
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
        return obj.favorite.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.in_shopping_cart.filter(user=request.user).exists()


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=1)


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
                ingredient=Ingredient.objects.get(id=item["id"]),
                amount=item["amount"]
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipeingredient_list)

    def validate_ingredients(self, value):
        ingredients = self.initial_data.get('ingredients')
        if len(ingredients) < 1:
            raise serializers.ValidationError(
                {'ingredients': 'empty'}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'required'}
            )
        ingredients_id_set = set(
            ingredient.get('id') for ingredient in ingredients)
        if len(ingredients_id_set) != len(value):
            raise serializers.ValidationError(
                {'ingredients': 'id duplicated'}
            )
        for ingredient in value:
            ingredient_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    {'ingredients': f'id {ingredient_id} not exists'}
                )
        return value

    def create(self, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data
        )
        self.__save_ingredients(recipe, ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        recipe = super().update(instance, validated_data)
        if ingredients_data:
            recipe.ingredients.all().delete()
            self.__save_ingredients(recipe, ingredients_data)
        else:
            raise serializers.ValidationError(
                'ingredients required'
            )
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
