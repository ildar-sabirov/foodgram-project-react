from django.contrib import admin

from .models import (
    Ingredient, Tag, Recipe, IngredientRecipe, FavoriteRecipe,
    ShoppingCartRecipe
)

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(IngredientRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCartRecipe)
