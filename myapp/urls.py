from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, CustomAuthToken, TradeRequestViewSet
from .views import home, trade, register

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')  # Enables the new update_quantity route
router.register(r'trades', TradeRequestViewSet, basename='trade')

urlpatterns = [
    path('', home, name='home'),
    path('', include(router.urls)),
    path('trade/', trade, name='trade'),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('register/', register, name='register'),
]
