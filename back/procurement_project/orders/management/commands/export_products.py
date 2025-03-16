import csv
from django.core.management.base import BaseCommand
from orders.models import Product

class Command(BaseCommand):
    help = 'Экспорт товаров в CSV файл'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу для сохранения товаров')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        products = Product.objects.select_related('supplier').all()

        fieldnames = ['supplier_username', 'supplier_name', 'name', 'description', 'price', 'category']
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for product in products:
                writer.writerow({
                    'supplier_username': product.supplier.user.username,
                    'supplier_name': product.supplier.company_name,
                    'name': product.name,
                    'description': product.description,
                    'price': str(product.price),
                    'category': product.custom_fields.get('category', '')
                })

        self.stdout.write(self.style.SUCCESS(f'Экспорт товаров завершен. Файл сохранен в {csv_file}'))
