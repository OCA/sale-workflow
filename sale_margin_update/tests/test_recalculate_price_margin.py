# Copyright 2024 SDi Sidoo Soluciones S.L. <www.sidoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestRecalculatePriceMargin(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "standard_price": 50.0,
            }
        )
        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 10,
                "price_unit": 100.0,
                "purchase_price": 50.0,
            }
        )
        cls.wizard = cls.env["sale.recalculate.price.margin"].create(
            {
                "sale_margin_percent": 20,
                "order_id": cls.sale_order.id,
            }
        )

    def test_onchange_sale_margin_percent_negative(self):
        with self.assertRaises(UserError):
            self.wizard.sale_margin_percent = -10
            self.wizard._onchange_sale_margin_percent()

    def test_onchange_sale_margin_percent_greater_than_100(self):
        with self.assertRaises(UserError):
            self.wizard.sale_margin_percent = 110
            self.wizard._onchange_sale_margin_percent()

    def test_recalculate_price_margin(self):
        self.wizard.recalculate_price_margin()
        self.assertAlmostEqual(self.sale_order_line.price_unit, 62.5, places=2)

    def test_recalculate_price_margin_with_line_id(self):
        self.wizard.line_id = self.sale_order_line
        self.wizard.recalculate_price_margin()
        self.assertAlmostEqual(self.sale_order_line.price_unit, 62.5, places=2)

    def test_recalculate_price_margin_with_100_percent_margin(self):
        self.wizard.sale_margin_percent = 100
        self.wizard.recalculate_price_margin()
        self.assertAlmostEqual(self.sale_order_line.price_unit, 100.0, places=2)

    def test_recalculate_price_margin_with_0_percent_margin(self):
        self.wizard.sale_margin_percent = 0
        self.wizard.recalculate_price_margin()
        self.assertAlmostEqual(self.sale_order_line.price_unit, 50.0, places=2)

    def test_open_wizard_from_sale_order(self):
        action = self.sale_order.wizard_price_unit_by_margin()
        self.assertEqual(action["res_model"], "sale.recalculate.price.margin")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["context"]["default_order_id"], self.sale_order.id)

    def test_open_wizard_from_sale_order_line(self):
        action = self.sale_order_line.wizard_price_unit_by_margin()
        self.assertEqual(action["res_model"], "sale.recalculate.price.margin")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["context"]["default_line_id"], self.sale_order_line.id)
