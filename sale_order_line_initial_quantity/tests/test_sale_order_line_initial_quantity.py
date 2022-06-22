# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestSaleOrderLineInitialQuantity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ==== Sale Orders ====
        cls.order1 = cls.env.ref("sale.sale_order_1")
        cls.order1.action_confirm()
        # ==== Sale Order Lines====
        cls.line = cls.order1.order_line[0]

    def test_update_sale_order_line_qty(self):
        self.assertFalse(self.order1.initial_qty_changed)
        self.assertEqual(self.line.product_uom_qty, self.line.product_uom_initial_qty)
        # change the product quantity
        self.line.write({"product_uom_qty": 9.0})
        self.assertEqual(self.line.product_uom_initial_qty, 3.0)
        self.assertTrue(self.order1.initial_qty_changed)
