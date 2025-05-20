from django.contrib.auth import get_user_model
from rest_framework import serializers


from recipes.serializers import SimpleRecipeSerializer
from .serializers import CustomUserSerializer
from .models import Subscription


User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author',)

    def validate(self, attrs):
        if attrs.get('user') == attrs.get('author'):
            raise serializers.ValidationError('self subcription')
        return super().validate(attrs)

    def to_representation(self, instance):
        serializer = CustomUserSerializer(
            instance.author, context=self.context)
        result = serializer.data.copy()
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = instance.author.recipes.all()
        result['recipes_count'] = len(recipes)
        if recipes_limit:
            recipes = recipes[0:int(recipes_limit)]
        recipe_serializer = SimpleRecipeSerializer(
            recipes, many=True, context=self.context)
        result['recipes'] = recipe_serializer.data
        return result
