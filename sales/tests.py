from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from inventory.models import Category, Product
from sales.models import Sale, SaleItem

User = get_user_model()


class SaleAndSaleItemModelTests(TestCase):

    def setUp(self):
        self.cat = Category.objects.create(name="Snacks")
        self.product1 = Product.objects.create(
            category=self.cat,
            name="Chips",
            sku="CHIPZ",
            cost_price=Decimal("1.00"),
            sell_price=Decimal("2.50"),
            quantity=50,
        )
        self.product2 = Product.objects.create(
            category=self.cat,
            name="Candy",
            sku="CANDY",
            cost_price=Decimal("0.50"),
            sell_price=Decimal("1.25"),
            quantity=100,
        )
        self.user = User.objects.create_user(username="cashier1", password="pass")

    def test_sale_str_format(self):
        sale = Sale.objects.create(cashier=self.user)
        self.assertIn("Sale #", str(sale))
        self.assertIn(str(sale.id), str(sale))
        self.assertIn(str(sale.datetime.year), str(sale))

    def test_sale_ordering(self):
        s1 = Sale.objects.create(cashier=self.user, datetime=timezone.now())
        s2 = Sale.objects.create(
            cashier=self.user, datetime=timezone.now() + timezone.timedelta(minutes=5)
        )
        sales = list(Sale.objects.all())
        self.assertEqual(sales, [s2, s1])

    def test_sale_total_initial_zero(self):
        sale = Sale.objects.create(cashier=self.user)
        self.assertEqual(sale.total, Decimal("0.00"))

    def test_saleitem_save_sets_price_and_line_total(self):
        sale = Sale.objects.create(cashier=self.user)
        item = SaleItem.objects.create(sale=sale, product=self.product1, quantity=2)
        self.assertEqual(item.price, self.product1.sell_price)
        self.assertEqual(item.line_total, item.price * item.quantity)

    def test_saleitem_decreases_product_quantity(self):
        sale = Sale.objects.create(cashier=self.user)
        initial_qty = self.product1.quantity
        item = SaleItem.objects.create(sale=sale, product=self.product1, quantity=7)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, initial_qty - 7)

    def test_saleitem_recalc_total_on_save(self):
        sale = Sale.objects.create(cashier=self.user)
        SaleItem.objects.create(sale=sale, product=self.product1, quantity=3)
        SaleItem.objects.create(sale=sale, product=self.product2, quantity=2)
        sale.refresh_from_db()
        expected_total = (
            self.product1.sell_price * 3 + self.product2.sell_price * 2
        ).quantize(Decimal("0.01"))
        self.assertEqual(sale.total, expected_total)

    def test_recalc_total_method(self):
        sale = Sale.objects.create(cashier=self.user)
        item1 = SaleItem.objects.create(sale=sale, product=self.product1, quantity=1)
        item2 = SaleItem.objects.create(sale=sale, product=self.product2, quantity=2)
        # fudge the line_total and check method
        item2.line_total = Decimal("999.99")
        item2.save(force_update=True)
        sale.recalc_total()
        sale.refresh_from_db()
        expected_total = item1.line_total + item2.line_total
        self.assertEqual(sale.total, expected_total)

    def test_saleitem_update_does_not_decrease_quantity(self):
        sale = Sale.objects.create(cashier=self.user)
        item = SaleItem.objects.create(sale=sale, product=self.product1, quantity=5)
        qty_after_first = self.product1.quantity
        # Now update the item, should not reduce product again
        item.quantity = 10
        item.save(force_update=True)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, qty_after_first)

    def test_saleitem_line_total_always_updated(self):
        sale = Sale.objects.create(cashier=self.user)
        item = SaleItem.objects.create(sale=sale, product=self.product2, quantity=4)
        old_line_total = item.line_total
        item.price = Decimal("2.00")
        item.quantity = 3
        item.save(force_update=True)
        item.refresh_from_db()
        self.assertEqual(item.line_total, item.price * item.quantity)
        self.assertNotEqual(item.line_total, old_line_total)

    def test_saleitem_no_negative_quantity_on_product(self):
        # Try to oversell
        sale = Sale.objects.create(cashier=self.user)
        self.product1.quantity = 3
        self.product1.save()
        item = SaleItem.objects.create(sale=sale, product=self.product1, quantity=10)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 0)

    def test_product_quantity_update_field_only(self):
        sale = Sale.objects.create(cashier=self.user)
        item = SaleItem.objects.create(sale=sale, product=self.product2, quantity=2)
        item.product.refresh_from_db()
        self.assertEqual(item.product.quantity, 98)

    def test_created_and_updated_fields_exist(self):
        sale = Sale.objects.create(cashier=self.user)
        item = SaleItem.objects.create(sale=sale, product=self.product1, quantity=1)
        self.assertIsNotNone(sale.created_at)
        self.assertIsNotNone(sale.updated_at)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)
