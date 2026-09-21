from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderShowCurrencyRate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_currency = cls.env.company.currency_id
        cls.foreign_currency = (
            cls.env["res.currency"]
            .with_context(active_test=False)
            .search([("id", "!=", cls.company_currency.id)], limit=1)
        )
        cls.foreign_currency.active = True
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.pricelist_foreign = cls.env["product.pricelist"].create(
            {
                "name": "Foreign Pricelist",
                "currency_id": cls.foreign_currency.id,
            }
        )

    def setUp(self):
        super().setUp()
        self.env.company.sale_order_currency_report_id = False

    def _create_order(self, pricelist=None):
        vals = {"partner_id": self.partner.id}
        if pricelist:
            vals["pricelist_id"] = pricelist.id
        return self.env["sale.order"].create(vals)

    def _create_rate(self, currency, rate):
        return self.env["res.currency.rate"].create(
            {
                "currency_id": currency.id,
                "rate": rate,
                "name": fields.Date.today(),
                "company_id": self.env.company.id,
            }
        )

    def test_show_when_foreign_currency_and_rate(self):
        order = self._create_order(pricelist=self.pricelist_foreign)
        self.assertEqual(order.currency_id, self.foreign_currency)
        self.assertTrue(order._show_currency_rate_in_report())

    def test_hide_when_same_currency(self):
        order = self._create_order()
        self.assertEqual(order.currency_id, self.company_currency)
        self.assertFalse(order._show_currency_rate_in_report())

    def test_show_when_same_currency_with_reference_and_rate(self):
        self.env.company.sale_order_currency_report_id = self.foreign_currency
        self._create_rate(self.foreign_currency, 0.2)
        order = self._create_order()
        self.assertEqual(order.currency_id, self.company_currency)
        self.assertTrue(order._show_currency_rate_in_report())

    def test_hide_when_same_currency_with_reference_but_no_rate(self):
        self.env.company.sale_order_currency_report_id = self.foreign_currency
        self.env["res.currency.rate"].search(
            [
                ("currency_id", "=", self.foreign_currency.id),
                ("company_id", "=", self.env.company.id),
            ]
        ).unlink()
        order = self._create_order()
        self.assertFalse(order._show_currency_rate_in_report())

    def test_report_rate_from_currency_uses_reference(self):
        self.env.company.sale_order_currency_report_id = self.foreign_currency
        self._create_rate(self.foreign_currency, 0.2)
        order = self._create_order()
        self.assertEqual(order._get_report_rate_from_currency(), self.foreign_currency)

    def test_report_display_rate_uses_reference_currency(self):
        self.env.company.sale_order_currency_report_id = self.foreign_currency
        self._create_rate(self.foreign_currency, 0.2)
        order = self._create_order()
        rate = order._get_report_display_rate()
        self.assertGreater(rate, 0)
