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