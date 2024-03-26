# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestSaleOrderQtyToInvoiceCancelled(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "list_price": 10.0,
                "taxes_id": False,
                "invoice_policy": "order",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "list_price": 20.0,
                "taxes_id": False,
                "invoice_policy": "order",
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "list_price": 30.0,
                "taxes_id": False,
                "invoice_policy": "delivery",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "John Doe",
            }
        )

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

        cls.sol1 = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product1.id,
                "name": "Product 1",
                "product_uom_qty": 1.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "discount": 10.0,
                "order_id": cls.so.id,
            }
        )
        cls.sol2 = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product2.id,
                "name": "Product 2",
                "product_uom_qty": 2.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "order_id": cls.so.id,
            }
        )

    def test_generate_credit_note_after_cancellation(self):
        # Create the invoice
        self.so.action_confirm()
        invoice = self.so._create_invoices(final=True)
        invoice.action_post()
        self.assertEqual(len(self.so.invoice_ids), 1)
        self.assertEqual(self.so.invoice_ids, invoice)
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.move_type, "out_invoice")

        # Cancel the order
        self.assertEqual(
            self.so.with_context(disable_cancel_warning=True).action_cancel(), True
        )
        self.assertEqual(self.so.state, "cancel")
        self.assertEqual(len(self.so.invoice_ids), 1)

        # Create the credit note
        refund = self.so._create_invoices(final=True)
        self.assertTrue(refund)
        refund.action_post()

        self.assertEqual(len(self.so.invoice_ids), 2)
        self.assertEqual(self.so.invoice_ids - invoice, refund)
        self.assertEqual(refund.state, "posted")
        self.assertEqual(refund.move_type, "out_refund")

        self.assertEqual(invoice.amount_total, refund.amount_total)
        self.assertEqual(
            set(invoice.invoice_line_ids.mapped("name")),
            set(refund.invoice_line_ids.mapped("name")),
        )

    def test_generate_credit_note_only_for_order_invoice_policy(self):
        self.sol3 = self.env["sale.order.line"].create(
            {
                "product_id": self.product3.id,
                "name": "Product 3",
                "product_uom_qty": 3.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "order_id": self.so.id,
            }
        )

        # Create the invoice
        self.so.action_confirm()
        # Deliver the product 3
        self.so.picking_ids.move_lines.write({"quantity_done": 3.0})
        self.so.picking_ids.button_validate()

        invoice = self.so._create_invoices(final=True)
        invoice.action_post()
        self.assertEqual(len(self.so.invoice_ids), 1)
        self.assertEqual(self.so.invoice_ids, invoice)
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.move_type, "out_invoice")

        # Cancel the order
        self.assertEqual(
            self.so.with_context(disable_cancel_warning=True).action_cancel(), True
        )
        self.assertEqual(self.so.state, "cancel")
        self.assertEqual(len(self.so.invoice_ids), 1)

        # Create the credit note
        refund = self.so._create_invoices(final=True)
        self.assertTrue(refund)
        refund.action_post()

        self.assertEqual(len(self.so.invoice_ids), 2)
        self.assertEqual(self.so.invoice_ids - invoice, refund)
        self.assertEqual(refund.state, "posted")
        self.assertEqual(refund.move_type, "out_refund")

        self.assertNotEqual(invoice.amount_total, refund.amount_total)
        self.assertNotEqual(
            set(invoice.invoice_line_ids.mapped("name")),
            set(refund.invoice_line_ids.mapped("name")),
        )
        self.assertEqual(
            invoice.line_ids.mapped("product_id"),
            (self.product1 | self.product2 | self.product3),
        )
        self.assertEqual(
            refund.line_ids.mapped("product_id"),
            (self.product1 | self.product2),
        )

    def test_regenerate_credit_note_after_cancellation(self):
        # Create the invoice
        self.so.action_confirm()
        invoice = self.so._create_invoices(final=True)
        invoice.action_post()
        self.assertEqual(
            self.so.with_context(disable_cancel_warning=True).action_cancel(), True
        )
        self.assertEqual(self.so.state, "cancel")

        # Create the credit note
        refund = self.so._create_invoices(final=True)
        self.assertTrue(refund)
        refund.action_post()

        # Regenerate the credit note
        with self.assertRaises(UserError):
            self.so._create_invoices(final=True)
