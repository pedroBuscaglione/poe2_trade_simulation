from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Item, TradeRequest, OnlineStatus
from .serializers import ItemSerializer, TradeRequestSerializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # O app usa o token para autenticar, então retorna só os itens do usuário logado
        return Item.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Garante que o item criado será do usuário logado
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
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
    return render(request, 'myapp/home.html')

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
    meus_itens = Item.objects.filter(owner=request.user)

    online_users = OnlineStatus.objects.filter(is_online=True).exclude(user=request.user)
    online_user_ids = online_users.values_list('user_id', flat=True)

    outros_itens = Item.objects.filter(owner__id__in=online_user_ids)

    return render(request, 'myapp/trade.html', {
        'meus_itens': meus_itens,
        'outros_itens': outros_itens
    })

@csrf_exempt
@login_required
def set_online(request):
    OnlineStatus.objects.update_or_create(user=request.user, defaults={'is_online': True})
    return JsonResponse({"status": "online"})

@csrf_exempt
@login_required
def set_offline(request):
    OnlineStatus.objects.update_or_create(user=request.user, defaults={'is_online': False})
    return JsonResponse({"status": "offline"})

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