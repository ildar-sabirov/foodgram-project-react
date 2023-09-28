from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet

app_name = 'api'

router_v1 = DefaultRouter()

# router_v1.register(r'users', UserViewSet, basename='user')
router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
