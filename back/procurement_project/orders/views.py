from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Product, Order, Cart, CartItem
from .serializers import ProductSerializer, OrderSerializer, CartSerializer, CartItemSerializer, UserSerializer
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

# Регистрация пользователя
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Список товаров
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Детали товара
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Работа с корзиной
class CartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            CartItem.objects.create(cart=cart, **serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "Не указан product_id"}, status=status.HTTP_400_BAD_REQUEST)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Создание заказа
class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        # Отправка email с подтверждением клиенту
        send_mail(
            subject='Подтверждение заказа',
            message=f'Ваш заказ #{order.id} принят. Спасибо за покупку!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.request.user.email],
        )
        # Отправка накладной администратору
        send_mail(
            subject='Новый заказ',
            message=f'Заказ #{order.id} от {self.request.user.username}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )

# Список заказов
class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role == 'customer':
            return Order.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'supplier':
            return Order.objects.filter(items__product__supplier__user=self.request.user).distinct()
        return Order.objects.none()

# Детали заказа
class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# Обновление статуса заказа
class OrderStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Некорректный статус"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
