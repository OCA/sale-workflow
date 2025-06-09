from odoo.tests.common import TransactionCase
from odoo import fields


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
        # Use currency._convert for expected result
        conversion_date = (
            self.sale_order.date_order and self.sale_order.date_order.date()
            or fields.Date.context_today(self.sale_order)
        )
        expected = self.sale_order.currency_id._convert(
            self.sale_order.amount_total,
            self.sale_order.company_id.currency_id,
            self.sale_order.company_id,
            conversion_date,
        )
        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected,
            places=2,
            msg="Amount in company currency should be converted using _convert method.",
        )

    def test_03_amount_total_curr_reversed_currency(self):
        """Test conversion when company currency is EUR and sale order is USD."""
        # Create a new company with EUR currency to avoid UserError
        new_company = self.env['res.company'].create({
            'name': 'TestCo EUR',
            'currency_id': self.currency_eur.id,
        })
        # Reassign order to new company
        self.sale_order.company_id = new_company
        # Ensure company_currency_id is updated
        self.assertEqual(
            self.sale_order.company_currency_id,
            self.currency_eur,
            msg="Company currency should be EUR."
        )
        # Sale currency USD
        self.sale_order.currency_id = self.currency_usd
        self.sale_order._compute_amount_company()
        # Expected USD->EUR conversion
        conversion_date = (
            self.sale_order.date_order and self.sale_order.date_order.date()
            or fields.Date.context_today(self.sale_order)
        )
        expected = self.sale_order.currency_id._convert(
            self.sale_order.amount_total,
            self.sale_order.company_id.currency_id,
            self.sale_order.company_id,
            conversion_date,
        )
        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected,
            places=2,
            msg="Reversed conversion using _convert should match expected."
        )
