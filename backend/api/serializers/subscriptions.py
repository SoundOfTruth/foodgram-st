from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers.recipes import SimpleRecipeSerializer
from api.serializers.users import CustomUserSerializer
from recipes.models import Recipe
from users.models import Subscription


User = get_user_model()


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            'user',
            'author',
        )

    def validate(self, attrs):
        if attrs.get('user') == attrs.get('author'):
            raise serializers.ValidationError('self subcription')
        return super().validate(attrs)

    def to_representation(self, instance):
        author = instance.author
        serializer = SubscriptionSerializer(author, context=self.context)
        return serializer.data


class SubscriptionSerializer(CustomUserSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        payload = CustomUserSerializer(instance, context=self.context).data
        recipes = Recipe.objects.filter(author=instance)
        payload['recipes_count'] = len(recipes)
        if recipes_limit:
            try:
                recipes = recipes[: int(recipes_limit)]
            except ValueError:
                raise serializers.ValidationError(
                    {'recipes_limit': 'Не является числом'}
                )
        payload['recipes'] = SimpleRecipeSerializer(recipes, many=True).data
        return payload
