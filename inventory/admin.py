from django.contrib import admin
from .models import Category, Customers, Stock, StockHistory

# Register your models here.


admin.site.register(Category)
admin.site.register(Customers)
admin.site.register(Stock)
admin.site.register(StockHistory)