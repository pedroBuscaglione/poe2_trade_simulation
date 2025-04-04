from rest_framework import generics
from .models import Item
from .serializers import ItemSerializer
from django.http import HttpResponse

class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemRetrieveDelete(generics.RetrieveDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

def home(request):
    return HttpResponse("Welcome to the PoE Trade API!")