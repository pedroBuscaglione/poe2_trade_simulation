from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    rarity = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='items')

    def __str__(self):
        return f"{self.name} ({self.rarity}) x{self.quantity}"

class TradeRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    from_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="offered_item")
    to_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="requested_item")

    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} ↔ {self.to_user.username} ({self.status})"
    
class OnlineStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"