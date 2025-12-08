# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleCancelConfirmed(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SaleOrder = cls.env["sale.order"]
        cls.env.company.write({"enable_sale_cancel_restrict": True})
        cls.partner = cls.env["res.partner"].create({"name": "Test Parnter"})
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "invoice_policy": "order", "is_storable": True}
        )
        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 8,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )

        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.location, 10)

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
        self.sale_order.picking_ids.move_line_ids.quantity = 8
        self.sale_order.picking_ids.button_validate()
        self.assertEqual(self.sale_order.picking_ids.state, "done")
        with self.assertRaises(ValidationError):
            self.sale_order.action_cancel()
