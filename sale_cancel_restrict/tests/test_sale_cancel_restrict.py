# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleCancelConfirmed(TransactionCase):
    def setUp(self):
        super(TestSaleCancelConfirmed, self).setUp()
        SaleOrder = self.env["sale.order"]
        self.env.company.write({"enable_sale_cancel_restrict": True})
        self.partner = self.env["res.partner"].create({"name": "Test Parnter"})
        self.location = self.env.ref("stock.stock_location_stock")
        self.product = self.env["product.product"].create(
            {"name": "Test product", "invoice_policy": "order", "type": "product"}
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

        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10
        )

    def test_01_sale_order_cancel_invoice(self):
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        with self.assertRaises(ValidationError):
            self.sale_order.action_cancel()
        self.sale_order.invoice_ids.button_cancel()
        self.sale_order.action_cancel()
        self.assertEqual(
            self.sale_order.state, "cancel", "The sale order should be canceled"
        )
        self.assertEqual(
            self.sale_order.invoice_ids.state,
            "cancel",
            "The invoice should be canceled",
        )

    def test_02_sale_order_cancel_transfer(self):
        self.sale_order.action_confirm()
        self.sale_order.picking_ids.action_assign()
        self.sale_order.picking_ids.move_line_ids.qty_done = 8
        self.sale_order.picking_ids.button_validate()
        self.assertEqual(self.sale_order.picking_ids.state, "done")
        with self.assertRaises(ValidationError):
            self.sale_order.action_cancel()
