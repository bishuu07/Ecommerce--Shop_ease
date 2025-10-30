from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Product(models.Model):
    MATERIAL_CHOICES = [
        ('gold', 'Gold'), ('silver', 'Silver'), ('handmade', 'Handmade'),
        ('gemstone', 'Gemstone'), ('pearl', 'Pearl'), ('other', 'Other')
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title


class Wishlist(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        product = models.ForeignKey('Product', on_delete=models.CASCADE)
        added_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            unique_together = ('user', 'product')  # One per product

        def __str__(self):
            return f"{self.user.username} ♥ {self.product.title}"