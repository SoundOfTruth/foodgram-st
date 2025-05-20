from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet
from recipes import views


router = DefaultRouter()
router.register('ingredients', views.IngridientViewSet, basename='ingredient')
router.register('recipes', views.RecipeViewSet, basename='recipe')
user_router = DefaultRouter()
user_router.register('users', CustomUserViewSet, basename='user')


urlpatterns = [
    path('', include(user_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
