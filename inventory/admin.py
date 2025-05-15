from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "product_count")
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "quantity", "sell_price", "is_low")
    list_filter = ("category",)  # sidebar filter
    search_fields = ("name", "sku")
    list_editable = ("quantity", "sell_price")  # ro‘yxatda to‘g‘ridan tahrir
    readonly_fields = ("cost_price",)  # faqat ko‘rish
    ordering = ("name",)

    @admin.display(boolean=True, description="Low?")
    def is_low(self, obj):
        return obj.quantity <= obj.min_stock
