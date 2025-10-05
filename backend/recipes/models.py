from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from constants import (
    MAX_INGREDIENT_NAME_LENGTH,
    MAX_INGREDIENT_MEASUREMENT_UNIT_LENGTH,
    MAX_RECIPE_NAME_LENGTH,
    MIN_AMOUNT_LENGTH,
    MIN_COOKING_TIME_LENGTH,
)


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=MAX_INGREDIENT_NAME_LENGTH, unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_INGREDIENT_MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT_LENGTH),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = (
            'recipe',
            'ingredient',
        )
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe}({self.recipe.pk}) : {self.ingredient}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор'
    )
    image = models.ImageField(verbose_name='Фото', upload_to='recipes/images/')
    name = models.CharField(verbose_name='Название', max_length=MAX_RECIPE_NAME_LENGTH)
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=[
            MinValueValidator(MIN_COOKING_TIME_LENGTH),
        ],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.author}: {self.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.recipe}({self.recipe.pk})'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='shopping_cart_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.recipe}({self.recipe.pk})   '
