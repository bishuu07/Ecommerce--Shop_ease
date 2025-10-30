# products/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from django.shortcuts import redirect
from cart.models import CartItem

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Filters
    material = request.GET.get('material')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('q')

    if material:
        products = products.filter(material=material)
    if category_id:
        products = products.filter(category_id=category_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search:
        products = products.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    context = {
        'products': products,
        'categories': categories,
        'materials': [choice[0] for choice in Product.MATERIAL_CHOICES],
        'selected_material': material,
        'selected_category': category_id,
        'search_query': search,
    }
    return render(request, 'products/home.html', context)

#def product_detail(request, pk):
    #product = get_object_or_404(Product, pk=pk)
   # return render(request, 'products/detail.html', {'product': product})

# products/views.py
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Check cart status
    in_cart = False
    cart_quantity = 1
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(user=request.user, product=product).first()
        if cart_item:
            in_cart = True
            cart_quantity = cart_item.quantity

    # Check wishlist status
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'in_cart': in_cart,
        'cart_quantity': cart_quantity,
        'is_in_wishlist': is_in_wishlist,  # ← SEND THIS
    }
    return render(request, 'products/detail.html', context)


@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('products:product_detail', pk=pk)

@login_required
def remove_from_wishlist(request, pk):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product__pk=pk)
    wishlist_item.delete()
    return redirect('products:product_detail', pk=pk)

def wishlist_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'wishlist_items': items})