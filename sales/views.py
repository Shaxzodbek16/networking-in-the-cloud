from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from .models import Sale
from .forms import SaleForm, SaleItemFormSet


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "sales/sale_list.html"
    context_object_name = "sales"
    paginate_by = 25


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "sales/sale_detail.html"


class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "sales/sale_form.html"
    success_url = reverse_lazy("sale_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            form.fields["cashier"].queryset = form.fields["cashier"].queryset.filter(
                id=self.request.user.id
            )
            form.initial["cashier"] = self.request.user
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = SaleItemFormSet(self.request.POST)
        else:
            context["items"] = SaleItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context["items"]
        if items.is_valid():
            self.object = form.save()
            items.instance = self.object
            items.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
