# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


class TestSaleStockCancelRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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

    def test_cancel_sale_order_restrict(self):
        """Validates the picking and do the assertRaises cancelling the
        order for checking that it's forbidden
        """
        self.picking.button_validate()
        with self.assertRaises(UserError):
            self.sale_order.action_cancel()

    def test_cancel_sale_order_ok(self):
        """Don't validate the picking and cancel the order, being completed."""
        # check the status of invoices after cancelling the order
        self.sale_order.action_cancel()
        self.assertEqual(
            self.sale_order.picking_ids.state,
            "cancel",
            "After cancelling a picking, the state should be cancelled",
        )
