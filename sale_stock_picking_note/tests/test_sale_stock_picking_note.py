# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common


class TestSaleStockPickingNote(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
                "picking_note": "<p>Test note</p>",
                "picking_customer_note": "Test customer note",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product"}
        )

    def test_01_sale_to_picking_note(self):
        """Pass note to picking from SO"""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1})
                ],
            }
        )
        order.picking_note = "This note goes to the picking..."
        order.picking_customer_note = "Picking comment"
        order.action_confirm()
        self.assertEqual(order.picking_ids[:1].note, order.picking_note)
        self.assertEqual(
            order.picking_ids[:1].customer_note, order.picking_customer_note
        )
        report = self.env.ref("stock.action_report_delivery")
        res = str(
            report._render_qweb_html(
                "stock.action_report_delivery", order.picking_ids.ids
            )[0]
        )
        self.assertRegex(res, "Picking comment")

    def test_02_sale_to_picking_note(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1
        self.assertEqual(sale_order_form.picking_note, self.partner.picking_note)
        self.assertEqual(
            sale_order_form.picking_customer_note, self.partner.picking_customer_note
        )
        sale_order = sale_order_form.save()
        sale_order.action_confirm()
        self.assertEqual(sale_order.picking_ids[:1].note, self.partner.picking_note)
        self.assertEqual(
            sale_order.picking_ids[:1].customer_note,
            self.partner.picking_customer_note,
        )
        report = self.env.ref("stock.action_report_delivery")
        res = str(
            report._render_qweb_html(
                "stock.action_report_delivery", sale_order.picking_ids.ids
            )[0]
        )
        self.assertRegex(res, self.partner.picking_customer_note)

    def test_03_sale_to_picking_note(self):
        # If create manually a outgoing picking, check if notes are passed
        picking_out_form = Form(self.env["stock.picking"])
        picking_out_form.picking_type_id = self.env.ref("stock.picking_type_out")
        picking_out_form.partner_id = self.partner
        with picking_out_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 1
        self.assertEqual(picking_out_form.note, self.partner.picking_note)
        self.assertEqual(
            picking_out_form.customer_note, self.partner.picking_customer_note
        )
        picking_out_form.save()
        report = self.env.ref("stock.action_report_delivery")
        res = str(
            report._render_qweb_html(
                "stock.action_report_delivery", picking_out_form.id
            )[0]
        )
        self.assertRegex(res, self.partner.picking_customer_note)
        # If create manually a incoming picking, notes are not passed
        picking_in_form = Form(self.env["stock.picking"])
        picking_in_form.picking_type_id = self.env.ref("stock.picking_type_in")
        picking_in_form.partner_id = self.partner
        with picking_out_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 1
        self.assertNotEqual(picking_in_form.note, self.partner.picking_note)
        self.assertNotEqual(
            picking_in_form.customer_note, self.partner.picking_customer_note
        )
        picking_in_form.save()
        report = self.env.ref("stock.action_report_delivery")
        res = str(
            report._render_qweb_html(
                "stock.action_report_delivery", picking_in_form.id
            )[0]
        )
        self.assertNotRegex(res, self.partner.picking_customer_note)
