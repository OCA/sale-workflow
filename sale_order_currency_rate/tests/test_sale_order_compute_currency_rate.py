# copyright 2024 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).

from odoo.tests.common import TransactionCase


class TestSaleOrderCurrencyRate(TransactionCase):
    def setUp(cls):
        super().setUp()
        cls.company = cls.env["res.company"].create({"name": "Test Company"})
        cls.partner = cls.env["res.partner"].create({"name": "Test client"})
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")
        cls.company.currency_id = cls.currency_usd
        cls.product = cls.env.ref("product.product_product_9")
        cls.sale_order = cls.env["sale.order"].create(
            {
                "company_id": cls.company.id,
                "currency_id": cls.currency_eur.id,
                "date_order": "2024-08-30",
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        cls.sale_order.currency_id = cls.currency_eur

    def test_compute_currency_rate_same_currency(self):
        self.sale_order.currency_id = self.currency_usd
        self.sale_order._compute_currency_rate()
        self.assertEqual(self.sale_order.currency_rate, 1.0)
        self.assertEqual(self.sale_order.inverse_currency_rate, 1.0)

    def test_compute_currency_rate_conversion(self):
        self.sale_order._compute_currency_rate()
        expected_rate = self.currency_eur._convert(
            1.0,
            self.currency_usd,
            self.company,
            self.sale_order.date_order,
            round=False,
        )
        expected_inverse_rate = self.currency_usd._convert(
            1.0,
            self.currency_eur,
            self.company,
            self.sale_order.date_order,
            round=False,
        )
        self.assertEqual(self.sale_order.currency_rate, expected_rate)
        self.assertEqual(self.sale_order.inverse_currency_rate, expected_inverse_rate)
