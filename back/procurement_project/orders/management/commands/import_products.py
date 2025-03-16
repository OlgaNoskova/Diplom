import csv
from django.core.management.base import BaseCommand
from orders.models import Product, Supplier
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Импорт товаров из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу с товарами')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                supplier_username = row.get('supplier_username')
                user, created = User.objects.get_or_create(username=supplier_username, defaults={'role': 'supplier'})
                supplier, _ = Supplier.objects.get_or_create(user=user, defaults={'company_name': row.get('supplier_name', 'Неизвестно')})
                Product.objects.create(
                    supplier=supplier,
                    name=row.get('name'),
                    description=row.get('description', ''),
                    price=row.get('price'),
                    custom_fields={'category': row.get('category', '')}
                )
        self.stdout.write(self.style.SUCCESS('Импорт товаров завершен'))
