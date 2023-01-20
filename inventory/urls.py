from django.urls import path
from . import views

appname = "index_page"

urlpatterns = [
    path('', views.index_page, name='home'),

    # category
    path("categories/", views.CategoryListView.as_view(), name='category_list'),
    path('new_category/', views.CategoryCreateView.as_view(), name='new_category'),
    path("category/<int:pk>/", views.CategoryDetailView.as_view(), name='category_detail'),
    path("category/<int:pk>/edit", views.CategoryUpdateView.as_view(), name='category_edit'),
    path("category/<int:pk>/delete", views.CategoryDeleteView.as_view(), name='category_delete'),

    # customers
    path("customer/", views.CustomerListView.as_view(), name='customer_list'),
    path('new_customer/', views.CustomerCreateView.as_view(), name='new_customer'),
    path("customer/<int:pk>/", views.CustomerDetailView.as_view(), name='customer_detail'),
    path("customer/<int:pk>/edit", views.CustomerUpdateView.as_view(), name='customer_edit'),
    path("customer/<int:pk>/delete", views.CustomerDeleteView.as_view(), name='customer_delete'),
]