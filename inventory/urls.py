from django.urls import path
from . import views

appname = "index_page"

urlpatterns = [
    path('', views.index_page, name='home'),
    path("categories/", views.CategoryListView.as_view(), name='category_list'),
    path('new_category/', views.CategoryCreateView.as_view(), name='new_category'),
    path("category/<int:pk>/", views.CategoryDetailView.as_view(), name='category_detail'),
    path("category/<int:pk>/edit", views.CategoryUpdateView.as_view(), name='category_edit'),
    path("category/<int:pk>/delete", views.CategoryDeleteView.as_view(), name='category_delete'),
]