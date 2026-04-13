from django.contrib import admin
from .models import MockProduct, MockOrder


@admin.register(MockProduct)
class MockProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name',)


@admin.register(MockOrder)
class MockOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'status', 'quantity', 'created_at')
    list_filter = ('status',)
    search_fields = ('product__name', 'user__email')
