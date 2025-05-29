from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from constants import (
    MAX_LENTH_INGREDIENT_NAME_LENGTH,
    MAX_LENTH_INGREDIENT_MEASUREMENT_UNIT_LENGTH)


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENTH_INGREDIENT_NAME_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENTH_INGREDIENT_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe_ingredients', verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1),],
    )
    constraints = [
        models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_recipe_ingredient'
        )
    ]

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe}({self.recipe.pk}) : {self.ingredient}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes', verbose_name='Автор',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='recipes/images/',
        blank=False,
        null=False
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=256)
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.author}: {self.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites', verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites', verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.recipe}({self.recipe.pk})'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_carts', verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_carts', verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe}({self.recipe.pk}) : {self.ingredient}'
