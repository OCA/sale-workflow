# Copyright 2013 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestSaleCancelReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        SaleOrder = cls.env["sale.order"]
        CancelReason = cls.env["sale.order.cancel.reason"]

        cls.reason = CancelReason.create({"name": "Canceled for tests"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "sale_ok": True,
                "standard_price": 99.9,
            }
        )
        cls.sale_order_1 = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_uom_qty": 8})
                ],
            }
        )

        cls.sale_order_2 = cls.sale_order_1.copy()
        cls.sale_orders = cls.sale_order_1 + cls.sale_order_2

    def test_sale_order_cancel_reason(self):
        """
        - Cancel a sales order with the wizard asking for the reason.
        - Then the sale order should be canceled and the reason stored.
        """
        SaleOrderCancel = self.env["sale.order.cancel.wizard"]
        wizard = SaleOrderCancel.create(
            {"reason_id": self.reason.id, "order_id": self.sale_order_1.id}
        )
        wizard.with_context(
            active_model="sale.order", active_ids=self.sale_order_1.id
        ).action_cancel()
        self.assertEqual(
            self.sale_order_1.state, "cancel", "the sale order should be canceled"
        )
        self.assertEqual(self.sale_order_1.cancel_reason_id.id, self.reason.id)

    def test_sale_order_cancel_reason_mass_cancel(self):
        MassCancelOrders = self.env["sale.mass.cancel.orders"]
        wizard = MassCancelOrders.with_context(
            active_model="sale.order", active_ids=self.sale_orders.ids
        ).create({"reason_id": self.reason.id})
        wizard.action_mass_cancel()

        self.assertRecordValues(
            self.sale_orders,
            [
                {"cancel_reason_id": self.reason.id},
                {"cancel_reason_id": self.reason.id},
            ],
        )

    def test_sale_order_cancel_draft(self):
        """
        When the order is canceled and then turned back to "draft", the cancellation
         reason should be removed.
        """
        with Form.from_action(
            self.env, self.sale_order_1.action_cancel_wizard()
        ) as form:
            form.reason_id = self.reason
            wizard = form.save()

        wizard.action_cancel()

        self.assertEqual(self.sale_order_1.state, "cancel")
        self.assertEqual(self.sale_order_1.cancel_reason_id, self.reason)

        self.sale_order_1.action_draft()

        self.assertEqual(self.sale_order_1.state, "draft")
        self.assertFalse(self.sale_order_1.cancel_reason_id)
