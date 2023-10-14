from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тэга'
    )
    color = ColorField(
        max_length=7,
        verbose_name='Цвет тэга'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг тэга'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время - 1')]
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(1, 'Минимальное количество - 1')]
    )

    class Meta:
        verbose_name = 'Ингредиенты для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'Для рецепта "{self.recipe}" понадобиться "{self.ingredient}"'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт "{self.recipe}" в избранное'


class ShoppingCartRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в список покупок'
