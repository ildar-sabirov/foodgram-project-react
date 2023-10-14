from django.contrib import admin

from .models import (
    Ingredient, Tag, Recipe, IngredientRecipe, FavoriteRecipe,
    ShoppingCartRecipe
)

admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCartRecipe)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (IngredientRecipeInline,)

    def favorite_count(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
