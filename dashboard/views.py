from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDay
from django.contrib.auth import get_user_model

from inventory.models import Category, Product
from sales.models import Sale, SaleItem

User = get_user_model()


def dashboard_view(request):
    # Metrics
    total_sales_count = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum("total"))["total"] or 0
    total_products = Product.objects.filter(is_active=True).count()
    active_users = User.objects.filter(is_active=True).count()

    # Sales Over Time (last 30 days)
    since = timezone.now() - timedelta(days=30)
    raw_sales = (
        Sale.objects.filter(datetime__gte=since)
        .annotate(day=TruncDay("datetime"))
        .values("day")
        .annotate(total_sales=Count("id"), total_revenue=Sum("total"))
        .order_by("day")
    )
    sales_over_time = [
        {
            "day": entry["day"].strftime("%Y-%m-%d"),
            "total_sales": entry["total_sales"],
            "total_revenue": float(entry["total_revenue"] or 0),
        }
        for entry in raw_sales
    ]

    # Inventory By Category
    raw_inv = (
        Category.objects.annotate(product_count=Count("products"))
        .values("name", "product_count")
        .order_by("name")
    )
    inventory_by_category = [
        {"name": c["name"], "product_count": c["product_count"]} for c in raw_inv
    ]

    # Low Stock Products
    low_stock_qs = Product.objects.filter(quantity__lte=F("min_stock")).values(
        "name", "quantity", "min_stock", "sku", category_name=F("category__name")
    )
    low_stock_products = list(low_stock_qs)

    # Category Revenue
    raw_cat_rev = (
        SaleItem.objects.values("product__category__name")
        .annotate(revenue=Sum(F("quantity") * F("price")))
        .order_by("-revenue")
    )
    category_revenue = [
        {"category": r["product__category__name"], "revenue": float(r["revenue"] or 0)}
        for r in raw_cat_rev
    ]

    # Top Selling Products
    raw_top = (
        SaleItem.objects.values("product__name")
        .annotate(
            total_qty=Sum("quantity"), total_revenue=Sum(F("quantity") * F("price"))
        )
        .order_by("-total_qty")[:5]
    )
    top_selling_products = [
        {
            "name": p["product__name"],
            "total_qty": p["total_qty"],
            "total_revenue": float(p["total_revenue"] or 0),
        }
        for p in raw_top
    ]

    # User Distribution
    raw_users = User.objects.values("role").annotate(count=Count("id"))
    user_distribution = [{"role": u["role"], "count": u["count"]} for u in raw_users]

    # Top Performing Staff
    raw_staff = (
        Sale.objects.values("cashier__username", "cashier__role")
        .annotate(revenue=Sum("total"), transactions=Count("id"))
        .order_by("-revenue")[:5]
    )
    top_staff = [
        {
            "username": s["cashier__username"],
            "role": s["cashier__role"],
            "revenue": float(s["revenue"] or 0),
            "transactions": s["transactions"],
        }
        for s in raw_staff
    ]

    context = {
        "total_sales_count": total_sales_count,
        "total_revenue": total_revenue,
        "total_products": total_products,
        "active_users": active_users,
        "sales_over_time": sales_over_time,
        "inventory_by_category": inventory_by_category,
        "low_stock_products": low_stock_products,
        "category_revenue": category_revenue,
        "top_selling_products": top_selling_products,
        "user_distribution": user_distribution,
        "top_staff": top_staff,
    }
    return render(request, "dashboard/index.html", context)
