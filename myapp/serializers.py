from rest_framework import serializers
from .models import Item, TradeRequest

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class TradeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeRequest
        fields = '__all__'
        read_only_fields = ['from_user', 'status', 'created_at']
