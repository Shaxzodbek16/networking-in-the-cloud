from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from django.contrib import messages


from .models import Product, Category
from .forms import ProductForm, CategoryForm


class StaffOrAdminMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.role in ("admin", "manager", "staff")


class CategoryListView(LoginRequiredMixin, StaffOrAdminMixin, ListView):
    model = Category
    template_name = "inventory/category_list.html"
    context_object_name = "categories"
    paginate_by = 10


class CategoryCreateView(
    LoginRequiredMixin, StaffOrAdminMixin, CreateView
):  # ← faqat CreateView
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("category_list")


class CategoryUpdateView(
    LoginRequiredMixin, StaffOrAdminMixin, UpdateView
):  # ← faqat UpdateView
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("category_list")


class CategoryDeleteView(LoginRequiredMixin, StaffOrAdminMixin, DeleteView):
    model = Category
    template_name = "inventory/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")


class ProductListView(LoginRequiredMixin, StaffOrAdminMixin, ListView):
    model = Product
    template_name = "inventory/product_list.html"
    paginate_by = 10
    queryset = Product.objects.filter(is_active=True)


class ProductCreateView(
    LoginRequiredMixin, StaffOrAdminMixin, CreateView
):  # ✅ faqat CreateView
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"


class ProductUpdateView(LoginRequiredMixin, StaffOrAdminMixin, UpdateView):
    model = Product
    form_class = ProductForm


class ProductDeleteView(LoginRequiredMixin, StaffOrAdminMixin, View):
    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Product, pk=kwargs["pk"])
        obj.is_active = False
        obj.save(update_fields=["is_active"])
        messages.success(request, "Mahsulot arxivga o‘tkazildi 👍")
        return redirect("product_list")

    def get(self, request, *args, **kwargs):
        self.post(request, *args, **kwargs)
        return redirect("product_list")
