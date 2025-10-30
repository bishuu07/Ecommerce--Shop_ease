# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart
from .models import CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    quantity = int(request.POST.get('quantity', 1))

    # Check stock
    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} items in stock!")
        return redirect('products:product_detail', pk=product_id)

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # If already in cart → increase quantity
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f"Cannot add more. Only {product.stock} in stock!")
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Updated {product.title} quantity to {new_quantity}")
    else:
        messages.success(request, f"Added {quantity} x {product.title} to cart")

    return redirect('products:product_detail', pk=product_id)

@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        elif quantity > cart_item.product.stock:
            messages.error(request, f"Only {cart_item.product.stock} in stock!")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated.")
    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_name = cart_item.product.title
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart.")
    return redirect('cart:cart_detail')