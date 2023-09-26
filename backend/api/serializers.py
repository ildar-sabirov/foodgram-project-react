from rest_framework import serializers

from users.models import User

EMAIL_LENGTH = 254
USERNAME_LENGTH = 150


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с данными пользователей."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
        )
