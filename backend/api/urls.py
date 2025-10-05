from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.users import CustomUserViewSet
from api.views import recipes


router = DefaultRouter()
router.register('ingredients', recipes.IngridientViewSet, basename='ingredient')
router.register('recipes', recipes.RecipeViewSet, basename='recipe')
user_router = DefaultRouter()
user_router.register('users', CustomUserViewSet, basename='user')


urlpatterns = [
    path('', include(user_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
