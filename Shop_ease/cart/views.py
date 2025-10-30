# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart
from .models import CartItem
from django.contrib.auth.decorators import login_required

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product__id=product_id)
    cart_item.delete()
    return redirect('cart:cart_detail')