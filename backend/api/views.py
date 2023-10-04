from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, FavoriteRecipe
from .permissions import IsAdminOrReadOnly, IsAuthorOfRecipe
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer,
    FavoriteRecipeSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(
        detail=False, methods=['get'], url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def owner_profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        elif self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOfRecipe()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_recipe = FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        )
        if request.method == 'POST':
            if favorite_recipe:
                return Response(
                    {'error': 'Рецепт уже есть в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
                serializer = FavoriteRecipeSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if favorite_recipe:
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Рецепт не найден в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
