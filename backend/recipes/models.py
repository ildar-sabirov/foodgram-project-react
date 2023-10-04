from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200, blank=False)
    color = ColorField(max_length=7, blank=False)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, blank=False)
    measurement_unit = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False
    )
    image = models.ImageField(upload_to='recipes/images/', blank=False)
    name = models.CharField(max_length=200, blank=False)
    text = models.TextField(blank=False)
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        blank=False
    )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        blank=False
    )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} - {self.recipe}'
