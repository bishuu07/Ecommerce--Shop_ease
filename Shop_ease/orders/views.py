# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from cart.models import CartItem
from .models import Order, OrderItem
import requests

import logging
logger = logging.getLogger('orders')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    
    if total == 0:
        return redirect('cart:cart_detail')

    # Convert to paisa (Khalti uses paisa)
    amount_in_paisa = int(total * 100)

    context = {
        'cart_items': cart_items,
        'total': total,
        'amount_in_paisa': amount_in_paisa,
        'khalti_public_key': settings.KHALTI_PUBLIC_KEY,
    }
    return render(request, 'orders/checkout.html', context)

# orders/views.py
@login_required
def initiate_payment(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.total_price() for item in cart_items)
        payment_method = request.POST.get('payment_method', 'KHALTI')
        
        if total <= 0:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart:cart_detail')

        # === CREATE ORDER (PENDING) ===
        order = Order.objects.create(
            user=request.user,
            payment_method=payment_method,
            total_amount=total,
            status='PENDING'
        )

        # === CREATE ORDER ITEMS (NO STOCK CHANGE YET) ===
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(request, f"Not enough stock for '{item.product.title}'.")
                order.delete()
                return redirect('cart:cart_detail')

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # === CLEAR CART ===
        cart_items.delete()

        # === KHALTI PAYMENT ===
        if payment_method == 'KHALTI':
            payload = {
                "return_url": request.build_absolute_uri('/orders/verify/'),
                "website_url": request.build_absolute_uri('/'),
                "amount": int(total * 100),
                "purchase_order_id": str(order.id),
                "purchase_order_name": f"Order {order.id}",
                "customer_info": {
                    "name": request.user.get_full_name() or request.user.username,
                    "email": request.user.email or "user@example.com",
                    "phone": "9800000001"
                }
            }

            headers = {
                "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            try:
                response = requests.post(settings.KHALTI_INITIATE_URL, json=payload, headers=headers, timeout=10)
                data = response.json()

                if response.status_code == 200 and 'pidx' in data:
                    order.khalti_pidx = data['pidx']
                    order.save()
                    return redirect(data['payment_url'])
                else:
                    messages.error(request, "Failed to start payment. Please try again.")
                    order.delete()
                    return redirect('cart:cart_detail')

            except requests.RequestException as e:
                messages.error(request, "Payment gateway error.")
                order.delete()
                return redirect('cart:cart_detail')

        # === COD: SUCCESS IMMEDIATELY ===
        else:
            order.status = 'PENDING'  # Wait for delivery
            order.save()
            messages.success(request, 'Order placed! Pay on delivery.')
            return render(request, 'orders/success.html', {'order': order})

    return redirect('cart:cart_detail')

@login_required
def verify_payment(request):
    logger.debug("=== VERIFY PAYMENT STARTED ===")
    pidx = request.GET.get('pidx')
    order_id = request.GET.get('purchase_order_id')

    logger.debug(f"pidx: {pidx}, order_id: {order_id}")

    if not pidx or not order_id:
        messages.error(request, 'Invalid payment link.')
        return redirect('products:home')

    try:
        order = Order.objects.get(
            id=order_id,
            user=request.user,
            khalti_pidx=pidx,
            status='PENDING',
            payment_method='KHALTI'
        )
        logger.debug(f"Order found: {order.id}")

        # CORRECT: POST to /lookup/
        response = requests.post(
            settings.KHALTI_VERIFY_URL,
            json={"pidx": pidx},
            headers={"Authorization": f"Key {settings.KHALTI_SECRET_KEY}"},
            timeout=10
        )

        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Khalti data: {data}")

            if data.get('status') == 'Completed':
                # Reduce stock
                for item in order.items.all():
                    if item.product.stock >= item.quantity:
                        item.product.stock -= item.quantity
                        item.product.save()
                    else:
                        messages.error(request, f"Out of stock: {item.product.title}")
                        return render(request, 'orders/failure.html')

                order.status = 'PAID'
                order.save()
                messages.success(request, 'Payment successful!')
                return render(request, 'orders/success.html', {'order': order})

    except Order.DoesNotExist:
        logger.error("Order not found")
    except Exception as e:
        logger.exception("Verification failed")

    messages.error(request, 'Payment failed.')
    return render(request, 'orders/failure.html')