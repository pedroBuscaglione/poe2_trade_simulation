from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    rarity = models.CharField(max_length=50, default="Common")  # Example stat
    quantity = models.IntegerField(default=1)  # Stackable items

    def __str__(self):
        return f"{self.name} ({self.rarity})"
