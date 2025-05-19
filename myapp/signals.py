from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import OnlineStatus

@receiver(user_logged_in)
def marcar_online(sender, request, user, **kwargs):
    OnlineStatus.objects.update_or_create(user=user, defaults={"is_online": True})

@receiver(user_logged_out)
def marcar_offline(sender, request, user, **kwargs):
    OnlineStatus.objects.update_or_create(user=user, defaults={"is_online": False})