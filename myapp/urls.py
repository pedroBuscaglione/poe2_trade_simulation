from django.urls import path
from .views import ItemListCreate, ItemRetrieveDelete

urlpatterns = [
    path('items/', ItemListCreate.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemRetrieveDelete.as_view(), name='item-detail'),
]
