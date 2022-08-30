# Copyright 2013 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleCancelReason(TransactionCase):
    def test_sale_order_cancel_reason(self):
        """
        - Cancel a sales order with the wizard asking for the reason
        - Then the sale order should be canceled and the reason stored
        """
        SaleOrderCancel = self.env["sale.order.cancel"]
        context = {
            "active_model": "sale.order",
            "active_ids": [self.sale_order.id],
        }
        wizard = SaleOrderCancel.create(
            {"reason_id": self.reason.id, "order_id": self.sale_order.id}
        )
        wizard.with_context(**context).action_cancel()
        self.assertEqual(
            self.sale_order.state, "cancel", "the sale order should be canceled"
        )
        self.assertEqual(self.sale_order.cancel_reason_id.id, self.reason.id)

    def setUp(self):
        super(TestSaleCancelReason, self).setUp()
        SaleOrder = self.env["sale.order"]
        CancelReason = self.env["sale.order.cancel.reason"]
        self.reason = CancelReason.create({"name": "Canceled for tests"})
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_7")
        self.sale_order = SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 8})
                ],
            }
        )
