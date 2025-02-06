# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleStockCancelRestriction(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product test", "type": "consu", "is_storable": True}
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
        cls.picking.move_ids.quantity = 2

    def test_cancel_sale_order_restrict(self):
        """Validates the picking and do the assertRaises cancelling the
        order for checking that it's forbidden
        """
        self.picking.button_validate()
        with self.assertRaisesRegex(
            UserError, "You cannot cancel a stock move that has been set to 'Done'"
        ):
            self.sale_order.action_cancel()

    def test_cancel_sale_order_ok(self):
        """When canceling the order, the wizard is generated with the
        model 'sale.order.cancel
        """
        wizz = self.sale_order.action_cancel()
        self.assertEqual(
            wizz["res_model"],
            "sale.order.cancel",
        )
