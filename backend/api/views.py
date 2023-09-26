from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from .serializers import SignupSerializer, UserSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup_view(request):
    """Регистрация пользователя и отправка кода подтверждения по почте."""
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False, methods=['get', ], url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def owner_profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
