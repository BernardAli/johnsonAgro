import csv
import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from .forms import StockCreateForm, StockUpdateForm, IssueForm, ReceiveForm, StockHistorySearchForm, IssueCashForm, \
    ReceiveCashForm, CashHistorySearchForm
from .models import Category, Customers, Stock, StockHistory, Cash, CashHistory


def index_page(request):
    customers_count = Customers.objects.all().count()
    items_count = Stock.objects.all().count()
    recent_cash_activities = CashHistory.objects.all().order_by("-last_updated")[:10]
    recent_activities = StockHistory.objects.all().order_by("-last_updated")[:10]
    receivables = StockHistory.objects.values('sale_to').annotate(dcount=Sum('balance')).filter(dcount__gt=0)
    total_debt = StockHistory.objects.aggregate(Sum('balance'))['balance__sum']
    total_sales = StockHistory.objects.aggregate(Sum('total_sale_price'))['total_sale_price__sum']
    recent_sales = StockHistory.objects.filter(sale_quantity__gt=0).order_by("-last_updated")

    context = {
        'customers_count': customers_count,
        'items_count': items_count,
        'receivables': receivables,
        'total_debt': total_debt,
        "recent_sales": recent_sales,
        'total_sales': total_sales,
        'recent_activities': recent_activities,
        'recent_cash_activities': recent_cash_activities
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


def customer_details(request, pk):
    customer = Customers.objects.get(id=pk)
    recent_activities = StockHistory.objects.filter(sale_to__id=customer.id).order_by("-last_updated")
    recent_cash_activities = CashHistory.objects.filter(issue_by=customer.name).order_by("-last_updated")
    total_debt = StockHistory.objects.filter(sale_to__id=customer.id).aggregate(Sum('balance'))['balance__sum']
    total_sales = StockHistory.objects.filter(sale_to__id=customer.id).aggregate(Sum('total_sale_price'))['total_sale_price__sum']
    context = {
        'customer': customer,
        'recent_activities': recent_activities,
        'total_debt': total_debt,
        'total_sales': total_sales,
        'recent_cash_activities': recent_cash_activities
    }
    return render(request, 'inventory/customers_details.html', context)


# class CustomerDetailView(DetailView):
#     model = Customers
#     context_object_name = 'customer'
#     template_name = 'inventory/customers_details.html'


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


def list_receivables(request):
    debtors = StockHistory.objects.filter(balance__gt=0).order_by("-last_updated") | \
              StockHistory.objects.filter(balance__lt=0).order_by("-last_updated")
    context = {
        'debtors': debtors,
        'now':  datetime.datetime.now().astimezone()
    }
    return render(request, 'inventory/list_receivables.html', context)


def list_item(request):
    queryset = Stock.objects.all()
    context = {
        "queryset": queryset,
    }
    return render(request, "inventory/list_item.html", context)


def stock_detail(request, pk):
    queryset = Stock.objects.get(id=pk)
    context = {
        "title": queryset.item_name,
        "queryset": queryset,
    }
    return render(request, "inventory/stock_detail.html", context)


def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully Added')
        return redirect('list_items')
    context = {
        "form": form,
    }
    return render(request, "inventory/add_item.html", context)


def update_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = StockUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated')
            return redirect('list_items')

    context = {
        'form': form
    }
    return render(request, 'inventory/add_item.html', context)


def issue_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        if instance.unit_sale_price == 0:
            messages.success(request, "Price can not be zero")
        else:
            # instance.purchased_quantity = 0
            instance.total_sale_price = instance.unit_sale_price * instance.sale_quantity
            if instance.sale_quantity > instance.delivery_quantity:
                instance.quantity += instance.sale_quantity
                instance.yet_to_deliver += (instance.sale_quantity - instance.delivery_quantity)
            elif instance.delivery_quantity > instance.sale_quantity:
                instance.quantity += instance.sale_quantity
                instance.yet_to_deliver -= instance.delivery_quantity
            else:
                instance.quantity += instance.sale_quantity
            instance.total_sale_price = instance.sale_quantity * instance.unit_sale_price
            messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(
                instance.item_name) + "s sold")
            instance.save()
            issue_history = StockHistory(
                last_updated=instance.last_updated,
                category_id=instance.category_id,
                item_name=instance.item_name,
                waybill_number=instance.waybill_number,
                quantity=instance.quantity,
                sale_to=instance.sale_to,
                sale_by=instance.sale_by,
                sale_quantity=instance.sale_quantity,
                unit_sale_price=instance.unit_sale_price,
                total_sale_price=instance.total_sale_price,
                delivery_quantity=instance.delivery_quantity,
                payment_status=instance.payment_status,
                balance=instance.balance,
                receipt_no=instance.receipt_no,
            )
            issue_history.save()

        return redirect('list_items')
    # return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "queryset": queryset,
        "form": form,
    }
    return render(request, "inventory/add_item.html", context)


def receive_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        # instance.sale_quantity = 0
        instance.total_returned_price = instance.unit_returned_price * instance.returned_quantity
        instance.quantity -= instance.returned_quantity
        instance.total_returned_price = instance.unit_returned_price * instance.unit_returned_price
        instance.save()
        receive_history = StockHistory(
            last_updated=instance.last_updated,
            category_id=instance.category_id,
            item_name=instance.item_name,
            waybill_number=instance.waybill_number,
            quantity=instance.quantity,
            returned_quantity=instance.purchased_quantity,
            returned_by=instance.purchased_by,
            unit_returned_price=instance.unit_purchase_price,
            total_returned_price=instance.total_purchase_price,
        )
        receive_history.save()
        messages.success(request, "Returned SUCCESSFULLY. " + str(instance.quantity) + " " + str(
            instance.item_name) + "s now sold")

        return redirect('list_items')
    # return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "instance": queryset,
        "form": form,
        "username": 'Receive By: ' + str(request.user),
    }
    return render(request, "inventory/add_item.html", context)


def list_history(request):
    header = 'HISTORY DATA'
    queryset = StockHistory.objects.all().order_by("-last_updated")
    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    form = StockHistorySearchForm(request.POST or None)
    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
    }
    if request.method == 'POST':
        category = form['category'].value()
        # queryset = StockHistory.objects.filter(
        #     item_name__icontains=form['item_name'].value()
        # )

        queryset = StockHistory.objects.filter(
            item_name__icontains=form['item_name'].value(),
            last_updated__range=[
                form['start_date'].value(),
                form['end_date'].value()
            ]
        )

        if category != '':
            queryset = queryset.filter(category_id=category).order_by("-last_updated")

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['CATEGORY',
                 'RECEIPT NO',
                 'WAYBILL NO',
                 'ITEM NAME',
                 'QUANTITY',
                 'ISSUE QUANTITY',
                 'RECEIVE QUANTITY',
                 'RECEIVE BY',
                 'ISSUE BY',
                 'TOTAL SALE PRICE',
                 'TOTAL PURCHASE PRICE',
                 'LAST UPDATED'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                    [stock.category,
                     stock.receipt_no,
                     stock.waybill_number,
                     stock.item_name,
                     stock.quantity,
                     stock.sale_quantity,
                     stock.returned_quantity,
                     stock.returned_by,
                     stock.sale_by,
                     stock.total_sale_price,
                     stock.total_returned_price,
                     stock.last_updated])
            return response

        paginator = Paginator(queryset, 15)
        page_number = request.GET.get('page')
        queryset = paginator.get_page(page_number)

        context = {
            "form": form,
            "header": header,
            "queryset": queryset,
        }
    return render(request, "inventory/list_history.html", context)


def cash_item(request):

    queryset = Cash.objects.all()
    context = {
        "queryset": queryset,
    }

    return render(request, "inventory/cash_item.html", context)


def cash_detail(request, pk):
    queryset = Cash.objects.get(id=pk)
    context = {
        "queryset": queryset,
    }
    return render(request, "inventory/cash_detail.html", context)


def issue_cash(request, pk):
    queryset = Cash.objects.get(id=pk)
    form = IssueCashForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        if instance.amount_out > instance.balance:
            messages.success(request, "Not Enough Cash")
        else:
            # instance.purchased_quantity = 0
            instance.balance -= instance.amount_out
            instance.issue_by = str(request.user)
            messages.success(request, "Issued SUCCESSFULLY. " + str(instance.balance) + " " + str(
                instance.category) + " balance left")
            instance.save()
            cash_issue_history = CashHistory(
                last_updated=instance.last_updated,
                category=instance.category,
                detail=instance.detail,
                recipient=instance.recipient,
                issue_by=instance.issue_by,
                amount_out=instance.amount_out,
                created_on=instance.created_on,
                balance=instance.balance,
            )
            cash_issue_history.save()

        return redirect('cash_items')
    # return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "queryset": queryset,
        "form": form,
        "username": 'Issue By: ' + str(request.user),
    }
    return render(request, "inventory/add_item.html", context)


def receive_cash(request, pk):
    queryset = Cash.objects.get(id=pk)
    form = ReceiveCashForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        # instance.purchased_quantity = 0
        instance.balance += instance.amount_in
        messages.success(request, "Received SUCCESSFULLY. " + str(instance.balance) + " " + str(
            instance.category) + " balance left")
        instance.save()
        cash_receive_history = CashHistory(
            last_updated=instance.last_updated,
            category=instance.category,
            recipient=instance.recipient,
            detail=instance.detail,
            issue_by=instance.issue_by,
            amount_in=instance.amount_in,
            created_on=instance.created_on,
            balance=instance.balance,
        )
        cash_receive_history.save()

        return redirect('cash_items')

    context = {
        "queryset": queryset,
        "form": form,
        "username": 'Received By: ' + str(request.user),
    }
    return render(request, "inventory/add_item.html", context)


def cash_history(request):
    header = 'CASH HISTORY'
    queryset = CashHistory.objects.all()
    form = CashHistorySearchForm(request.POST or None)
    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
    }
    if request.method == 'POST':

        queryset = CashHistory.objects.filter(
            category__icontains=form['category'].value(),
            last_updated__range=[
                form['start_date'].value(),
                form['end_date'].value()
            ]
        )

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['CATEGORY',
                 'RECIPIENT',
                 'DETAIL',
                 'RECEIVED AMOUNT',
                 'PAID AMOUNT',
                 'BALANCE',
                 'ISSUED BY',
                 'LAST UPDATED'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                    [stock.category,
                     stock.recipient,
                     stock.detail,
                     stock.amount_in,
                     stock.amount_out,
                     stock.balance,
                     stock.issue_by,
                     stock.last_updated])
            return response

        context = {
            "form": form,
            "header": header,
            "queryset": queryset,
        }
    return render(request, "inventory/cash_history.html", context)