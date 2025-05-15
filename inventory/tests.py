from decimal import Decimal
from django.test import TestCase
from django.db.utils import IntegrityError, DataError
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Category, Product


class CategoryModelTests(TestCase):
    def test_category_str_returns_name(self):
        category = Category.objects.create(name="Food")
        self.assertEqual(str(category), "Food")

    def test_category_verbose_name_plural(self):
        self.assertEqual(Category._meta.verbose_name_plural, "Categories")

    def test_category_ordering(self):
        cat_b = Category.objects.create(name="Beverages")
        cat_a = Category.objects.create(name="Apparel")
        cats = Category.objects.all()
        self.assertEqual(list(cats), [cat_a, cat_b])

    def test_category_unique_name(self):
        Category.objects.create(name="Electronics")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Electronics")

    def test_category_blank_name(self):
        with self.assertRaises(ValidationError):
            cat = Category(name="")
            cat.full_clean()

    def test_category_long_name(self):
        cat = Category(name="a" * 61)
        with self.assertRaises(ValidationError):
            cat.full_clean()

    def test_category_update_name_to_existing(self):
        Category.objects.create(name="A")
        cat2 = Category.objects.create(name="B")
        cat2.name = "A"
        with self.assertRaises(IntegrityError):
            cat2.save()

    def test_category_products_related_name(self):
        cat = Category.objects.create(name="Snacks")
        prod = Product.objects.create(
            category=cat,
            name="Candy",
            sku="CANDY",
            cost_price=Decimal("1.00"),
            sell_price=Decimal("2.00"),
            quantity=10,
        )
        self.assertIn(prod, cat.products.all())

    def test_category_timestamps(self):
        cat = Category.objects.create(name="Pastries")
        self.assertIsNotNone(cat.created_at)
        self.assertIsNotNone(cat.updated_at)


class ProductModelTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Stationery")

    def test_product_str_returns_name(self):
        prod = Product.objects.create(
            category=self.cat,
            name="Pen",
            sku="PEN001",
            cost_price=Decimal("0.15"),
            sell_price=Decimal("0.35"),
            quantity=100,
        )
        self.assertEqual(str(prod), "Pen")

    def test_product_unique_together(self):
        Product.objects.create(
            category=self.cat,
            name="Pencil",
            sku="PENCIL01",
            cost_price=Decimal("0.10"),
            sell_price=Decimal("0.20"),
            quantity=50,
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                category=self.cat,
                name="Pencil",  # same name, same category!
                sku="PENCIL02",
                cost_price=Decimal("0.12"),
                sell_price=Decimal("0.22"),
                quantity=30,
            )

    def test_product_unique_name_in_different_category(self):
        cat2 = Category.objects.create(name="Art Supplies")
        Product.objects.create(
            category=self.cat,
            name="Eraser",
            sku="ERASER1",
            cost_price=Decimal("0.10"),
            sell_price=Decimal("0.20"),
            quantity=30,
        )
        try:
            Product.objects.create(
                category=cat2,
                name="Eraser",  # same name, different category: OK
                sku="ERASER2",
                cost_price=Decimal("0.12"),
                sell_price=Decimal("0.22"),
                quantity=10,
            )
        except IntegrityError:
            self.fail("IntegrityError raised for unique_together across categories")

    def test_product_ordering(self):
        p_b = Product.objects.create(
            category=self.cat,
            name="Binder",
            sku="BIND01",
            cost_price=Decimal("0.50"),
            sell_price=Decimal("1.00"),
            quantity=10,
        )
        p_a = Product.objects.create(
            category=self.cat,
            name="Agenda",
            sku="AGD01",
            cost_price=Decimal("1.00"),
            sell_price=Decimal("2.00"),
            quantity=15,
        )
        products = Product.objects.all()
        self.assertEqual(list(products), [p_a, p_b])

    def test_get_absolute_url(self):
        prod = Product.objects.create(
            category=self.cat,
            name="Marker",
            sku="MRK01",
            cost_price=Decimal("0.60"),
            sell_price=Decimal("1.20"),
            quantity=20,
        )
        self.assertEqual(prod.get_absolute_url(), reverse("product_list"))

    def test_is_low_property(self):
        prod = Product.objects.create(
            category=self.cat,
            name="Stapler",
            sku="STAP01",
            cost_price=Decimal("2.00"),
            sell_price=Decimal("3.00"),
            quantity=4,  # less than default min_stock (5)
        )
        self.assertTrue(prod.is_low)
        prod.quantity = 5
        prod.save()
        self.assertTrue(prod.is_low)
        prod.quantity = 6
        prod.save()
        self.assertFalse(prod.is_low)

    def test_min_stock_custom(self):
        prod = Product.objects.create(
            category=self.cat,
            name="Scissors",
            sku="SCISS01",
            cost_price=Decimal("0.80"),
            sell_price=Decimal("1.60"),
            quantity=9,
            min_stock=10,
        )
        self.assertTrue(prod.is_low)

    def test_is_active_default(self):
        prod = Product.objects.create(
            category=self.cat,
            name="Notebook",
            sku="NB01",
            cost_price=Decimal("0.40"),
            sell_price=Decimal("1.00"),
            quantity=10,
        )
        self.assertTrue(prod.is_active)

    def test_product_blank_name(self):
        with self.assertRaises(ValidationError):
            prod = Product(
                category=self.cat,
                name="",
                sku="X1",
                cost_price=Decimal("0.50"),
                sell_price=Decimal("1.00"),
                quantity=10,
            )
            prod.full_clean()

    def test_product_negative_quantity(self):
        with self.assertRaises(ValidationError):
            prod = Product(
                category=self.cat,
                name="TestNegQty",
                sku="NEGQTY",
                cost_price=Decimal("0.20"),
                sell_price=Decimal("0.40"),
                quantity=-3,
            )
            prod.full_clean()

    def test_product_long_name(self):
        prod = Product(
            category=self.cat,
            name="A" * 121,  # max_length=120
            sku="LONGSKU",
            cost_price=Decimal("0.50"),
            sell_price=Decimal("1.00"),
            quantity=10,
        )
        with self.assertRaises(ValidationError):
            prod.full_clean()

    def test_product_sku_required(self):
        with self.assertRaises(ValidationError):
            prod = Product(
                category=self.cat,
                name="NoSKU",
                cost_price=Decimal("0.50"),
                sell_price=Decimal("1.00"),
                quantity=10,
            )
            prod.full_clean()

    def test_product_decimal_precision(self):
        prod = Product.objects.create(
            category=self.cat,
            name="Precise",
            sku="PRECISE",
            cost_price=Decimal("0.123456"),
            sell_price=Decimal("2.999999"),
            quantity=2,
        )
        self.assertEqual(prod.cost_price, Decimal("0.123456"))
        self.assertEqual(prod.sell_price, Decimal("2.999999"))

    def test_product_update_quantity(self):
        prod = Product.objects.create(
            category=self.cat,
            name="UpdateMe",
            sku="UPD01",
            cost_price=Decimal("0.50"),
            sell_price=Decimal("1.50"),
            quantity=3,
        )
        prod.quantity = 99
        prod.save()
        prod.refresh_from_db()
        self.assertEqual(prod.quantity, 99)

    def test_product_timestamps(self):
        prod = Product.objects.create(
            category=self.cat,
            name="HasTime",
            sku="TIME01",
            cost_price=Decimal("0.50"),
            sell_price=Decimal("1.00"),
            quantity=1,
        )
        self.assertIsNotNone(prod.created_at)
        self.assertIsNotNone(prod.updated_at)

    def test_product_related_name(self):
        prod = Product.objects.create(
            category=self.cat,
            name="RelateMe",
            sku="REL01",
            cost_price=Decimal("0.50"),
            sell_price=Decimal("1.00"),
            quantity=1,
        )
        self.assertIn(prod, self.cat.products.all())
