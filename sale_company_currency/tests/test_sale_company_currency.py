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
                        {
                            "product_id": cls.product2.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    )
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
            self.sale_order.amount_total * self.sale_order.currency_rate, 2
        )
        self.assertEqual(
            amount_total_curr_rounded,
            amount_total_converted_rounded,
            msg=(
                "Amount in company currency should be converted "
                "using the currency rate."
            ),
        )
