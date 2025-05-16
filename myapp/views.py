from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Item, TradeRequest
from .serializers import ItemSerializer, TradeRequestSerializer
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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


class TradeRequestViewSet(viewsets.ModelViewSet):
    queryset = TradeRequest.objects.all()
    serializer_class = TradeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TradeRequest.objects.filter(to_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user, status='pending')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        trade = self.get_object()
        if trade.to_user != request.user:
            return Response({"error": "Permissão negada"}, status=403)

        # Trocar os itens entre os usuários
        trade.status = 'accepted'
        trade.save()

        # Atualizar donos dos itens
        trade.from_item.owner = trade.to_user
        trade.to_item.owner = trade.from_user
        trade.from_item.save()
        trade.to_item.save()

        return Response({"status": "accepted"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        trade = self.get_object()
        if trade.to_user != request.user:
            return Response({"error": "Permissão negada"}, status=403)

        trade.status = 'rejected'
        trade.save()
        return Response({"status": "rejected"})
    
@login_required
def trade_view(request):
    meu_inventario = Item.objects.filter(owner=request.user)
    outros_inventarios = Item.objects.exclude(owner=request.user)

    return render(request, 'myapp/trade.html', {
        'meus_itens': meu_inventario,
        'outros_itens': outros_inventarios
    })

@require_POST
@login_required
def enviar_troca(request):
    from_item_id = request.POST.get("from_item")
    to_item_id = request.POST.get("to_item")
    to_user_id = request.POST.get("to_user")

    try:
        from_item = Item.objects.get(id=from_item_id, owner=request.user)
        to_item = Item.objects.get(id=to_item_id)
        TradeRequest.objects.create(
            from_user=request.user,
            to_user_id=to_user_id,
            from_item=from_item,
            to_item=to_item
        )
    except Exception as e:
        print("Erro ao criar troca:", e)

    return redirect('trade')