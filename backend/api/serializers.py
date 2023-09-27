from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from users.models import User

# EMAIL_LENGTH = 254
# USERNAME_LENGTH = 150


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
    """Сериализатор для работы с данными пользователей."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name'
        )
