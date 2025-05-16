from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, CustomAuthToken, TradeRequestViewSet
from .views import home, trade_view, register, enviar_troca

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')  # Enables the new update_quantity route
router.register(r'trades', TradeRequestViewSet, basename='trade')

urlpatterns = [
    path('', home, name='home'),
    path('', include(router.urls)),
    path('trade/', trade_view, name='trade'),
    path('trade/send/', enviar_troca, name='enviar_troca'),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('register/', register, name='register'),
]
