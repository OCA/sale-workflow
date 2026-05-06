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

    def _create_order(self, pricelist=None):
        vals = {"partner_id": self.partner.id}
        if pricelist:
            vals["pricelist_id"] = pricelist.id
        return self.env["sale.order"].create(vals)

    def test_show_when_foreign_currency_and_rate(self):
        order = self._create_order(pricelist=self.pricelist_foreign)
        self.assertEqual(order.currency_id, self.foreign_currency)
        self.assertTrue(order._show_currency_rate_in_report())

    def test_hide_when_same_currency(self):
        order = self._create_order()
        self.assertEqual(order.currency_id, self.company_currency)
        self.assertFalse(order._show_currency_rate_in_report())
