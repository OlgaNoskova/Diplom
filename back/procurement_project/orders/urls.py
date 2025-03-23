from django.urls import path
from .views import (
    RegisterView, LoginView, ProductListView, ProductDetailView,
    CartView, OrderCreateView, OrderListView, OrderDetailView,
    OrderStatusUpdateView, ErrorTestView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('error-test/', ErrorTestView.as_view(), name='error-test'),
]
