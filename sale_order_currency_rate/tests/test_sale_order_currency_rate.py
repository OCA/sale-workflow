# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderCurrencyRate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner_id = cls.env.ref("base.res_partner_1")
        product_1 = cls.env.ref("product.product_product_4")
        product_2 = cls.env.ref("product.product_product_5")
        pricelist = cls.env.ref("product.list0")
        pricelist_data = pricelist.copy_data()[0]
        currency_eur = cls.env.ref("base.EUR")
        pricelist_data.update({"currency_id": currency_eur.id})
        cls.pricelist_eur = cls.env["product.pricelist"].create(pricelist_data)
        order_lines = [
            {"product_id": product_1.id, "product_uom_qty": 1},
            {"product_id": product_2.id, "product_uom_qty": 1},
        ]
        cls.order = cls.env["sale.order"].create(
            {
                "name": "SO Test",
                "partner_id": partner_id.id,
                "pricelist_id": pricelist.id,
                "order_line": [Command.create(line) for line in order_lines],
            }
        )

    def test_sale_order_currency_rate(self):
        # Setting the configuration to "both" in order to show currency rate and inverse
        # currency rate, when the pricelist of the order changes, it corresponds to
        # currency set in the pricelist.
        self.env["res.config.settings"].create({"sale_show_currency_rate": "both"})
        self.assertEqual(self.order.currency_rate, 1.0)
        self.assertEqual(self.order.inverse_currency_rate, 1.0)
        self.order.write({"pricelist_id": self.pricelist_eur.id})
        self.assertAlmostEqual(self.order.currency_rate, 0.65, places=2)
        self.assertAlmostEqual(self.order.inverse_currency_rate, 1.53, places=2)
