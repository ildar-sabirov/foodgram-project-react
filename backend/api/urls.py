from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')
router_v1.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('users/<int:pk>/subscribe/', UserViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'}
    )),
    path('users/subscriptions/', UserViewSet.as_view(
        {'get': 'subscriptions'}
    )),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
