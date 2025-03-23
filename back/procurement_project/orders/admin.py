from django.contrib import admin
from .models import Order, OrderItem, Product, Supplier
from django.core.mail import send_mail
from django.conf import settings

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'delivery_address', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'delivery_address')
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        updated = 0
        for order in queryset:
            if order.status != 'confirmed':
                order.status = 'confirmed'
                order.save()
                updated += 1
                send_mail(
                    subject='Статус заказа обновлен',
                    message=f'Ваш заказ #{order.id} теперь имеет статус: {order.get_status_display()}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.customer.email],
                )
        self.message_user(request, f'Обновлено заказов: {updated}')
    mark_as_confirmed.short_description = 'Перевести статус на "Подтвержден"'

    def mark_as_shipped(self, request, queryset):
        updated = 0
        for order in queryset:
            if order.status != 'shipped':
                order.status = 'shipped'
                order.save()
                updated += 1
                send_mail(
                    subject='Статус заказа обновлен',
                    message=f'Ваш заказ #{order.id} теперь имеет статус: {order.get_status_display()}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.customer.email],
                )
        self.message_user(request, f'Обновлено заказов: {updated}')
    mark_as_shipped.short_description = 'Перевести статус на "Отгружен"'

    def mark_as_delivered(self, request, queryset):
        updated = 0
        for order in queryset:
            if order.status != 'delivered':
                order.status = 'delivered'
                order.save()
                updated += 1
                send_mail(
                    subject='Статус заказа обновлен',
                    message=f'Ваш заказ #{order.id} теперь имеет статус: {order.get_status_display()}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.customer.email],
                )
        self.message_user(request, f'Обновлено заказов: {updated}')
    mark_as_delivered.short_description = 'Перевести статус на "Доставлен"'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    list_filter = ('order',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'supplier', 'price')
    list_filter = ('supplier',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'user')
    search_fields = ('company_name', 'user__username')
