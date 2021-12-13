# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, SavepointCase


class TestSaleStockCancelRestriction(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product test", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner test"})
        so_form = Form(cls.env["sale.order"])
        so_form.partner_id = cls.partner
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = cls.product
            soline_form.product_uom_qty = 2
        cls.sale_order = so_form.save()
        cls.sale_order.action_confirm()
        cls.picking = cls.sale_order.picking_ids
        cls.picking.move_lines.quantity_done = 2
        cls.picking.button_validate()

    def test_cancel_sale_order(self):
        with self.assertRaises(UserError):
            self.sale_order.action_cancel()
