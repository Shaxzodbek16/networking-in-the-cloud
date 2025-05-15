from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("line_total",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "datetime", "cashier", "total")
    list_filter = ("cashier",)
    date_hierarchy = "datetime"
    inlines = [SaleItemInline]

    # readonly total (avtomatik)
    readonly_fields = ("total",)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "product", "quantity", "price", "line_total")
    search_fields = ("product__name",)
