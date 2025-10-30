# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'id']
    actions = ['mark_shipped', 'mark_delivered']

    def mark_shipped(self, request, queryset):
        queryset.update(status='SHIPPED')
    mark_shipped.short_description = "Mark selected orders as Shipped"

    def mark_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
    mark_delivered.short_description = "Mark selected orders as Delivered"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']