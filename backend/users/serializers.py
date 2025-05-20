from django.contrib.auth import get_user_model
from djoser import serializers as d_serializers
from rest_framework import serializers


from api.fields import Base64ImageField


User = get_user_model()


class CustomUserSerializer(d_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.subscribers.filter(user=request.user).exists()


class CustomUserCreateSerializer(d_serializers.UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)


class LoginSerializer(d_serializers.UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
