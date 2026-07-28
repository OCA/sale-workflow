# Copyright 2025 APSL-Nagarro Bernat Obrador <borbador@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import TransactionCase


class TestNegativeDelivery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env["product.product"]
        SaleOrder = cls.env["sale.order"]
        Partner = cls.env["res.partner"]
        cls.partner = Partner.create({"name": "Test Partner"})

        cls.product = Product.create(
            {
                "name": "Test Product",
                "type": "product",
                "invoice_policy": "delivery",
                "tracking": "none",
            }
        )

        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
            }
        )

        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "product_uom_qty": -2.0,
                "product_uom": cls.product.uom_id.id,
                "price_unit": 10.0,
                "name": cls.product.name,
            }
        )

    def test_negative_delivery_update(self):
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids[0]
        move_line = picking.move_lines[0]
        move_line.quantity_done = 2.0

        picking.button_validate()

        self.sale_order_line.refresh()
        self.assertEqual(self.sale_order_line.qty_delivered, -2.0)
        invoice_wizard = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "delivered",
            }
        )
        invoice_wizard.with_context(active_ids=self.sale_order.ids).create_invoices()

        invoices = self.sale_order.invoice_ids
        self.assertEqual(len(invoices), 1)

        invoice = invoices[0]
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.product
        )

        self.assertEqual(len(invoice_line), 1)
        self.assertEqual(invoice_line.quantity, 2.0)
        self.assertEqual(invoice_line.price_unit, 10.0)
        self.assertEqual(invoice.amount_untaxed_signed, -20.0)
        self.assertEqual(invoice.move_type, "out_refund")

    def test_negative_and_positive_delivery_update(self):
        self.sale_order.action_confirm()
        positive_sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom": self.product.uom_id.id,
                "price_unit": 20.0,
                "name": self.product.name,
            }
        )
        # Should create 2 pickings, one for positive lines
        # because product is going out of stock
        # and another for negative lines because product is coming
        # back to stock
        self.assertEqual(len(self.sale_order.picking_ids), 2)
        return_picking = self.sale_order.picking_ids.filtered(
            lambda p: p.picking_type_code == "incoming"
        )
        out_picking = self.sale_order.picking_ids.filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        self.assertEqual(len(return_picking.move_lines), 1)
        self.assertEqual(len(out_picking.move_lines), 1)

        for picking in self.sale_order.picking_ids:
            for move_line in picking.move_lines:
                move_line.quantity_done = 2.0
            picking.button_validate()

        self.sale_order_line.refresh()
        self.assertEqual(self.sale_order_line.qty_delivered, -2.0)
        self.assertEqual(positive_sale_order_line.qty_delivered, 2.0)
        invoice_wizard = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "delivered",
            }
        )
        invoice_wizard.with_context(active_ids=self.sale_order.ids).create_invoices()

        invoices = self.sale_order.invoice_ids
        self.assertEqual(len(invoices), 1)

        invoice = invoices[0]
        invoice_lines = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.product
        )
        negative_invoice_line = invoice_lines[0]
        positive_invoice_line = invoice_lines[1]

        self.assertEqual(len(invoice_lines), 2)
        self.assertEqual(negative_invoice_line.quantity, -2.0)
        self.assertEqual(negative_invoice_line.price_unit, 10.0)
        self.assertEqual(negative_invoice_line.price_subtotal, -20.0)
        self.assertEqual(positive_invoice_line.quantity, 2.0)
        self.assertEqual(positive_invoice_line.price_unit, 20.0)
        self.assertEqual(positive_invoice_line.price_subtotal, 40.0)

        self.assertEqual(invoice.amount_untaxed_signed, 20.0)
        self.assertEqual(invoice.move_type, "out_invoice")
