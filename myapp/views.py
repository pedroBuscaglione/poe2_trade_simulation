from rest_framework.decorators import action
from rest_framework import viewsets, permissions
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
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Só retorna os itens do usuário autenticado
        return Item.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Ao criar um item, define automaticamente o owner
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        """Custom endpoint to update item quantity"""
        item = self.get_object()

        # Verifica se o item pertence ao usuário autenticado
        if item.owner != request.user:
            return Response({"error": "You do not have permission to modify this item."},
                            status=status.HTTP_403_FORBIDDEN)

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
def trade(request):
    items = Item.objects.filter(is_available=True).select_related('owner')
    return render(request, 'trade.html', {'items': items})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken. Please choose another.')
            else:
                form.save()
                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})