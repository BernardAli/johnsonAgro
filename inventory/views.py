from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from .models import Category, Customers


def index_page(request):
    customers_count = Customers.objects.all().count()
    context = {
        'customers_count': customers_count
    }
    return render(request, 'inventory/home.html', context)


class CategoryListView(ListView):
    template_name = 'inventory/category_list.html'
    model = Category
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'inventory/category_details.html'


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'inventory/category_create.html'
    fields = "__all__"
    success_url = reverse_lazy("category_list")


class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'inventory/category_create.html'
    fields = ['name', 'description']
    success_url = reverse_lazy("category_list")


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'inventory/category_delete.html'
    success_url = reverse_lazy("category_list")


class CustomerListView(ListView):
    template_name = 'inventory/customers_list.html'
    model = Customers
    context_object_name = 'customers'


class CustomerDetailView(DetailView):
    model = Customers
    template_name = 'inventory/customers_details.html'


class CustomerCreateView(CreateView):
    model = Customers
    template_name = 'inventory/customers_create.html'
    fields = "__all__"
    success_url = reverse_lazy("customer_list")


class CustomerUpdateView(UpdateView):
    model = Customers
    template_name = 'inventory/customers_create.html'
    fields = ['name', 'location', 'contact_no', 'category', 'country']
    success_url = reverse_lazy("customer_list")


class CustomerDeleteView(DeleteView):
    model = Customers
    template_name = 'inventory/customers_delete.html'
    success_url = reverse_lazy("customer_list")