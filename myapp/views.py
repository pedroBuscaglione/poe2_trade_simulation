from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import RegisterForm

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        """Custom endpoint to update item quantity"""
        item = self.get_object()
        new_quantity = request.data.get("quantity", None)

        if new_quantity is not None and int(new_quantity) >= 0:
            item.quantity = int(new_quantity)
            item.save()
            return Response(ItemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id, 'username': token.user.username})

def home(request):
    return render(request, 'home.html')

@login_required
def trade_list(request):
    items = Item.objects.all()
    return render(request, 'trade_list.html', {'items': items})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('home')  # or 'trade_list'
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})