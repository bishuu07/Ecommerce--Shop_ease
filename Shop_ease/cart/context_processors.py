# cart/context_processors.py
from .cart import Cart
from .models import CartItem
def cart(request):
    return {'cart': Cart(request)}

def cart_items_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_items_count': count}