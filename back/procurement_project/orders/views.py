from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.throttling import UserRateThrottle
from django.core.mail import send_mail
from django.conf import settings

# Импорт для авторизации через токены
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import Product, Order, Cart, CartItem
from .serializers import ProductSerializer, OrderSerializer, CartSerializer, CartItemSerializer, UserSerializer

from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint для регистрации пользователя.
    При регистрации пароль сохраняется в хешированном виде.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    throttle_classes = []  # отключаем тротлинг для регистрации

class LoginView(ObtainAuthToken):
    """
    API endpoint для авторизации пользователя. Возвращает токен.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk, 'username': user.username})

class ProductListView(generics.ListAPIView):
    """
    API endpoint для получения списка товаров.
    Применяется кэширование на 15 минут и тротлинг.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    throttle_classes = [UserRateThrottle]

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductDetailView(generics.RetrieveAPIView):
    """
    API endpoint для получения деталей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartView(views.APIView):
    """
    API endpoint для работы с корзиной пользователя.
    """
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

class OrderCreateView(generics.CreateAPIView):
    """
    API endpoint для создания заказа.
    Отправляет уведомления клиенту и администратору по email.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        # Отправка email клиенту
        send_mail(
            subject='Подтверждение заказа',
            message=f'Ваш заказ #{order.id} принят. Спасибо за покупку!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.request.user.email],
        )
        # Отправка email администратору
        send_mail(
            subject='Новый заказ',
            message=f'Заказ #{order.id} от {self.request.user.username}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )

class OrderListView(generics.ListAPIView):
    """
    API endpoint для получения списка заказов текущего пользователя.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role == 'customer':
            return Order.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'supplier':
            return Order.objects.filter(items__product__supplier__user=self.request.user).distinct()
        return Order.objects.none()

class OrderDetailView(generics.RetrieveAPIView):
    """
    API endpoint для получения деталей заказа.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    API endpoint для обновления статуса заказа.
    """
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

class ErrorTestView(views.APIView):
    """
    API endpoint для тестирования мониторинга ошибок (Sentry/Rollbar).
    При вызове генерирует исключение.
    """
    def get(self, request):
        raise Exception("Тестовое исключение для проверки мониторинга ошибок")
