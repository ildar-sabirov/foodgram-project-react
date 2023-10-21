from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCartRecipe, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOfRecipe
from .serializers import (FollowSerializer, IngredientSerializer,
                          ModifiedRecipeSerializer, RecipeSerializer,
                          TagSerializer)
from .utils import generate_shopping_cart_report

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=self.request.user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            subscription = Follow.objects.filter(
                user=self.request.user, following=author
            )
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=self.request.user)
        paginator = PageNumberPagination()
        authors = paginator.paginate_queryset(subscriptions, request)
        serializer = FollowSerializer(
            authors, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOfRecipe()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_action(self, model, user, pk, message):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe):
            return Response(
                {'error': 'Рецепт уже есть в {}.'.format(message)},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = ModifiedRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_action(self, model, user, pk, message):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe_is_existing = model.objects.filter(user=user, recipe=recipe)
        if recipe_is_existing:
            recipe_is_existing.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепт не найден в {}.'.format(message)},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        message = 'избранном'
        if request.method == 'POST':
            return self.post_action(FavoriteRecipe, request.user, pk, message)
        return self.delete_action(FavoriteRecipe, request.user, pk, message)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        message = 'списке покупок'
        if request.method == 'POST':
            return self.post_action(
                ShoppingCartRecipe, request.user, pk, message
            )
        return self.delete_action(
            ShoppingCartRecipe, request.user, pk, message
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit', 'amount')
        response = generate_shopping_cart_report(ingredients)
        return response
