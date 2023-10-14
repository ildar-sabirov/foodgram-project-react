import base64

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers, status
from djoser.serializers import UserCreateSerializer
from django.core.files.base import ContentFile

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientRecipe, FavoriteRecipe
)
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientRecipeSerializer(
        source='ingredient_recipes',
        read_only=True,
        many=True
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        cooking_time = data.get('cooking_time')
        if not ingredients:
            raise serializers.ValidationError(
                'Не был получен ингредиент для рецепта.'
            )
        ingredients_id_list = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_id = ingredient.get('id')
            if int(amount) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше единицы.'
                )
            if ingredient_id in ingredients_id_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            ingredients_id_list.append(ingredient_id)
        if not tags:
            raise serializers.ValidationError(
                'Не был получен тэг для рецепта.'
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тэги не должны повторяться.'
                )
            tags_list.append(tag)
        if cooking_time <= 0:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше единицы.'
            )
        return data

    @transaction.atomic
    def create_or_update_ingredients(self, recipe, ingredients):
        ingredient_objects = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_objects)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_or_update_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_or_update_ingredients(instance, ingredients)
        return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False


class ModifiedRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    recipes = ModifiedRecipeSerializer(
        many=True, read_only=True, source='recipe_set'
    )
    recipes_count = serializers.ReadOnlyField(source='recipe_set.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('username', 'email', 'first_name', 'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context['request'].user
        if Follow.objects.filter(following=author, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.',
                status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.',
                status.HTTP_400_BAD_REQUEST
            )
        return data
