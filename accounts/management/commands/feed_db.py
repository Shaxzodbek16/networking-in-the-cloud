import random, hashlib
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from accounts.models import User
from inventory.models import Category, Product
from sales.models import Sale, SaleItem


class Command(BaseCommand):
    help = "Populate demo DB: 1000 users, 10 categories, 100k products, 50k sales"

    USERS = 234
    CATEGORIES = 5
    PRODUCTS = 23894
    SALES = 12324

    def handle(self, *args, **kwargs):
        fake = Faker("en_US")
        Faker.seed(2025)
        fake.unique.clear()

        self._create_users(fake)
        categories = self._create_categories(fake)

        # generate random weights for categories (they sum to 1)
        weights = [random.random() for _ in categories]
        total = sum(weights)
        self.category_weights = [w / total for w in weights]

        products = self._create_products(fake, categories)
        # build a product popularity list (initially uniform, will drift over sales)
        self.product_popularity = [1] * len(products)

        self._create_sales(fake, products)
        self.stdout.write(self.style.SUCCESS("🎉  Demo data ready!"))

    def _create_users(self, fake: Faker):
        User.objects.exclude(is_superuser=True).delete()
        for _ in range(self.USERS):
            username = fake.unique.user_name()
            password = hashlib.sha256(username.encode()).hexdigest()[:10]
            role = random.choice(["admin", "staff", "manager"])
            User.objects.create_user(username=username, password=password, role=role)
        return User.objects.all()

    def _create_categories(self, fake: Faker):
        Category.objects.all().delete()
        cats = []
        for _ in range(self.CATEGORIES):
            name = fake.unique.word().title()
            cats.append(Category.objects.create(name=name))
        return cats

    def _create_products(self, fake: Faker, categories):
        Product.objects.all().delete()
        products = []
        for _ in range(self.PRODUCTS):
            idx = random.choices(
                range(len(categories)), weights=self.category_weights, k=1
            )[0]
            cat = categories[idx]

            name = f"{fake.color_name()} {fake.word().title()} {fake.unique.random_int(1, 99999):05}+{uuid.uuid4()}"
            sku = fake.unique.bothify(text="??#####").upper()
            cost = Decimal(fake.pydecimal(left_digits=2, right_digits=2, positive=True))
            sell = (cost * Decimal(random.uniform(1.2, 2.5))).quantize(Decimal("0.01"))
            qty = random.randint(0, 300)
            min_stock = random.randint(5, 50)

            prod = Product.objects.create(
                category=cat,
                name=name,
                sku=sku,
                cost_price=cost,
                sell_price=sell,
                quantity=qty,
                min_stock=min_stock,
            )
            products.append(prod)
        return products

    def _create_sales(self, fake: Faker, products):
        Sale.objects.all().delete()
        cashiers = list(User.objects.filter(role__in=["staff", "manager"]))

        for _ in range(self.SALES):
            sale = Sale.objects.create(
                cashier=random.choice(cashiers),
                datetime=fake.date_time_between(
                    start_date="-60d",
                    end_date="now",
                    tzinfo=timezone.get_current_timezone(),
                ),
            )

            # choose 1–5 line items, favoring popular products
            picks = random.choices(
                range(len(products)),
                weights=self.product_popularity,
                k=random.randint(1, 5),
            )
            for idx in picks:
                prod = products[idx]
                qty = random.randint(1, 10)
                item = SaleItem.objects.create(sale=sale, product=prod, quantity=qty)
                # bump that product’s popularity a bit
                self.product_popularity[idx] += qty

            sale.recalc_total()
