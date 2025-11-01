# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
]