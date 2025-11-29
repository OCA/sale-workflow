from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # currencies
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")

        # Customer
        cls.partner = cls.env.ref("base.res_partner_2")

        # Company
        cls.company = cls.env.ref("base.main_company")

        # Products
        cls.product1 = cls.env.ref("product.product_product_4")
        cls.product2 = cls.env.ref("product.product_product_5")

        # Create a sale order with the same currency as the company
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "company_id": cls.company.id,
                "currency_id": cls.currency_usd.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "product_uom_qty": 2,
                            "price_unit": 50.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )

    def test_01_amount_total_curr_same_currency(self):
        """Test amount_total_curr when sale order currency matches company currency."""
        self.sale_order.currency_id = self.currency_usd
        self.sale_order._compute_amount_company()
        self.assertEqual(
            self.sale_order.amount_total_curr,
            self.sale_order.amount_total,
            "Amount in company currency should match the total amount when currencies "
            "are the same.",
        )

    def test_02_amount_total_curr_different_currency(self):
        """Test amount_total_curr when sale order currency differs from company
        currency."""
        self.sale_order.currency_id = self.currency_eur
        self.sale_order._compute_amount_company()
        amount_total_curr_rounded = round(self.sale_order.amount_total_curr, 2)
        amount_total_converted_rounded = round(
            self.sale_order.amount_total / self.sale_order.currency_rate, 2
        )
        self.assertEqual(
            amount_total_curr_rounded,
            amount_total_converted_rounded,
            msg=(
                "Amount in company currency should be converted "
                "using the currency rate (division, not multiplication)."
            ),
        )

    def test_03_amount_total_curr_conversion_logic(self):
        """Test specific conversion logic to ensure division is used."""
        # Set up a specific scenario to test the conversion logic
        self.sale_order.currency_id = self.currency_eur
        # Set a specific currency rate for testing
        self.sale_order.currency_rate = 0.85  # 1 EUR = 0.85 USD

        # Calculate expected result: amount_total / currency_rate
        expected_amount = self.sale_order.amount_total / 0.85

        self.sale_order._compute_amount_company()

        # Verify the conversion uses division, not multiplication
        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected_amount,
            places=2,
            msg="Conversion should use division, not multiplication.",
        )

        # Verify that multiplication would give a different (wrong) result
        wrong_amount = self.sale_order.amount_total * 0.85
        self.assertNotAlmostEqual(
            self.sale_order.amount_total_curr,
            wrong_amount,
            places=2,
            msg="Multiplication should give different result than correct division.",
        )

    def test_04_amount_total_curr_rate_one(self):
        """Test conversion when currency_rate = 1 (should behave like same currency)."""
        self.sale_order.currency_id = self.currency_eur
        self.sale_order.currency_rate = 1.0

        self.sale_order._compute_amount_company()

        self.assertEqual(
            self.sale_order.amount_total_curr,
            self.sale_order.amount_total,
            "When currency_rate = 1, amount_total_curr should equal amount_total",
        )

    def test_05_amount_total_curr_extreme_rates(self):
        """Test conversion with very small and very large currency rates."""
        self.sale_order.currency_id = self.currency_eur

        # Test with very small rate (strong target currency)
        self.sale_order.currency_rate = 0.01  # 1 EUR = 0.01 USD
        self.sale_order._compute_amount_company()
        expected_small = self.sale_order.amount_total / 0.01
        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected_small,
            places=2,
            msg="Conversion with very small rate should work correctly",
        )

        # Test with very large rate (weak target currency)
        self.sale_order.currency_rate = 1000.0  # 1 EUR = 1000 USD
        self.sale_order._compute_amount_company()
        expected_large = self.sale_order.amount_total / 1000.0
        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected_large,
            places=2,
            msg="Conversion with very large rate should work correctly",
        )

    def test_06_amount_total_curr_multiple_orders(self):
        """Test computation with multiple sale orders in one batch."""
        # Create a second sale order
        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "currency_id": self.currency_eur.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_qty": 3,
                            "price_unit": 75.0,
                        },
                    )
                ],
            }
        )

        # Set different currency rates for both orders
        # First, change the currency of both orders to force conversion
        # Check what currency the company uses
        if self.company.currency_id == self.currency_usd:
            # Company uses USD, so use EUR for both orders
            self.sale_order.currency_id = self.currency_eur
            sale_order_2.currency_id = self.currency_eur
        else:
            # Company uses something else, use USD for both orders
            self.sale_order.currency_id = self.currency_usd
            sale_order_2.currency_id = self.currency_usd

        self.sale_order.currency_rate = 0.85
        sale_order_2.currency_rate = 1.20

        # Compute for both orders in batch
        orders = self.sale_order + sale_order_2
        orders._compute_amount_company()

        # Verify both orders computed correctly
        # Use the actual amount_total values from the orders
        expected_1 = self.sale_order.amount_total / 0.85
        expected_2 = sale_order_2.amount_total / 1.20

        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected_1,
            places=2,
            msg="First order should compute correctly in batch",
        )
        self.assertAlmostEqual(
            sale_order_2.amount_total_curr,
            expected_2,
            places=2,
            msg="Second order should compute correctly in batch",
        )

    def test_07_amount_total_curr_edge_cases(self):
        """Test edge cases like zero amount_total and extreme values."""
        self.sale_order.currency_id = self.currency_eur

        # Test with zero amount_total - set all line prices to zero
        for line in self.sale_order.order_line:
            line.price_unit = 0.0
        self.sale_order.currency_rate = 0.85

        self.sale_order._compute_amount_company()

        self.assertEqual(
            self.sale_order.amount_total_curr,
            0.0,
            "Zero amount_total should result in zero amount_total_curr",
        )

        # Reset to normal values
        self.sale_order.order_line[0].price_unit = 50.0
        if len(self.sale_order.order_line) > 1:
            self.sale_order.order_line[1].price_unit = 100.0
