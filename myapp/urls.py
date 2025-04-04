from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, CustomAuthToken
from .views import home, trade_list, register

router = DefaultRouter()
router.register(r'items', ItemViewSet)  # Enables the new update_quantity route

urlpatterns = [
    path('', home, name='home'),
    path('', include(router.urls)),
    path('trade/', trade_list, name='trade_list'),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('register/', register, name='register'),
]
