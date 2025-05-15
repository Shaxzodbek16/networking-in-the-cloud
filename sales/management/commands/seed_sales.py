from django.core.management.base import BaseCommand
from faker import Faker
import random
from accounts.models import User
from inventory.models import Product
from sales.models import Sale, SaleItem
from django.utils import timezone


class Command(BaseCommand):
    help = "Generate 5 000 random sales"

    def handle(self, *args, **kwargs):
        fake = Faker()
        cashiers = list(User.objects.filter(role__in=["staff", "manager"]))
        products = list(Product.objects.all())

        count = 0
        for _ in range(5000):
            sale = Sale.objects.create(
                cashier=random.choice(cashiers),
                datetime=fake.date_time_between(
                    start_date="-60d",
                    end_date="now",
                    tzinfo=timezone.get_current_timezone(),
                ),
            )
            for _ in range(random.randint(1, 5)):
                prod = random.choice(products)
                qty = random.randint(1, 10)
                SaleItem.objects.create(sale=sale, product=prod, quantity=qty)
            sale.recalc_total()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} sales created."))
