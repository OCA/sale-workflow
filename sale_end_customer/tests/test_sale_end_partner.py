# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleEndPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "service"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.end_customer = cls.env["res.partner"].create({"name": "End Customer"})

    def test_sale_order_invoice_field_propagation(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_end_customer_id": self.end_customer.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        sale_order.action_confirm()
        invoice_wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                **{"active_ids": [sale_order.id], "active_model": "sale.order"}
            )
            .create({"advance_payment_method": "delivered"})
        )
        invoice_wizard.create_invoices()
        invoice = self.env["account.move"].search(
            [("invoice_origin", "=", sale_order.name)], limit=1
        )
        self.assertTrue(invoice, "Invoice should be created.")
        self.assertEqual(
            invoice.partner_end_customer_id, sale_order.partner_end_customer_id
        )
