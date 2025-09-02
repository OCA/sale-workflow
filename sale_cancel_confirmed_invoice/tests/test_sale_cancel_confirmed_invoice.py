# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleCancelConfirmed(TransactionCase):
    def setUp(self):
        super(TestSaleCancelConfirmed, self).setUp()
        SaleOrder = self.env["sale.order"]
        self.env.company.write({"enable_sale_cancel_confirmed_invoice": True})
        self.partner = self.env["res.partner"].create({"name": "Test Parnter"})
        self.product = self.env["product.product"].create(
            {"name": "Test product", "invoice_policy": "order"}
        )
        self.sale_order = SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 8,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )

    def test_01_sale_order_cancel_confirmed_invoice(self):
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        self.sale_order.invoice_ids.action_post()
        self.assertEqual(
            self.sale_order.invoice_ids.state, "posted", "The invoice should be posted"
        )
        SaleOrderCancel = self.env["sale.order.cancel"]
        context = {
            "active_model": "sale.order",
            "active_ids": [self.sale_order.id],
        }
        wizard = SaleOrderCancel.create({"order_id": self.sale_order.id})
        wizard.with_context(**context).action_cancel()
        self.assertEqual(
            self.sale_order.state, "cancel", "The sale order should be canceled"
        )
        self.assertEqual(
            self.sale_order.invoice_ids.state,
            "cancel",
            "The invoice should be canceled",
        )
