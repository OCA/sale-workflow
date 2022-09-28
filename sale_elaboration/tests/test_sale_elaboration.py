# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestSaleElaboration(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Elaboration = cls.env["product.elaboration"]
        cls.product = cls.env["product.product"].create(
            {"name": "test", "tracking": "none", "list_price": 1000}
        )
        cls.product_elaboration_A = cls.env["product.product"].create(
            {
                "name": "Product Elaboration A",
                "type": "service",
                "list_price": 50.0,
                "invoice_policy": "order",
                "is_elaboration": True,
            }
        )
        cls.product_elaboration_B = cls.env["product.product"].create(
            {
                "name": "Product Elaboration B",
                "type": "service",
                "list_price": 25.0,
                "invoice_policy": "order",
                "is_elaboration": True,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "test - partner", "property_product_pricelist": cls.pricelist.id}
        )
        cls.elaboration_a = cls.Elaboration.create(
            {
                "code": "AA",
                "name": "Elaboration A",
                "product_id": cls.product_elaboration_A.id,
            }
        )
        cls.elaboration_b = cls.Elaboration.create(
            {
                "code": "BB",
                "name": "Elaboration B",
                "product_id": cls.product_elaboration_B.id,
            }
        )
        cls.order = cls._create_sale_order(cls, [(cls.product, 10, cls.elaboration_a)])

    def _create_sale_order(self, products_info):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        for product, qty, elaboration in products_info:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = qty
                if elaboration:
                    line_form.elaboration_id = elaboration
        return order_form.save()

    def test_search_elaboration(self):
        elaboration = self.Elaboration.name_search("Elaboration")
        self.assertEqual(len(elaboration), 2)
        elaboration = self.Elaboration.name_search("AA")
        self.assertEqual(len(elaboration), 1)

    def test_sale_elaboration_change(self):
        self.order.order_line.elaboration_id = self.elaboration_b.id
        self.assertEqual(self.order.order_line.elaboration_note, "Elaboration B")

    def test_sale_elaboration(self):
        self.order.action_confirm()
        self.order.picking_ids.move_lines.quantity_done = 10.0
        self.order.picking_ids._action_done()
        elaboration_lines = self.order.order_line.filtered("is_elaboration")
        self.assertEqual(len(elaboration_lines), 1)
        self.assertEqual(elaboration_lines.price_unit, 50.0)

    def test_sale_elaboration_multi(self):
        self.order.order_line.create(
            {
                "order_id": self.order.id,
                "product_id": self.product_elaboration_A.id,
                "product_uom_qty": 1.0,
                "price_unit": 50.0,
                "is_elaboration": True,
            }
        )
        self.order.action_confirm()
        self.order.picking_ids.move_lines.quantity_done = 10.0
        self.order.picking_ids._action_done()
        elaboration_lines = self.order.order_line.filtered("is_elaboration")
        self.assertEqual(len(elaboration_lines), 1)
        self.assertEqual(elaboration_lines.product_uom_qty, 11.0)

    def test_invoice_elaboration(self):
        self.order = self._create_sale_order(
            [
                (self.product_elaboration_A, 1, False),
                (self.product_elaboration_B, 1, False),
            ]
        )
        self.order.order_line.filtered(
            lambda l: l.product_id == self.product_elaboration_B
        ).is_elaboration = False
        self.order.action_confirm()
        invoice = self.order._create_invoices()
        so_line_elaboration = self.order.order_line.filtered("is_elaboration")
        so_line_no_elaboration = self.order.order_line - so_line_elaboration
        inv_line_elaboration = invoice.invoice_line_ids.filtered(
            lambda x: x.sale_line_ids == so_line_elaboration
        )
        inv_line_no_elaboration = invoice.invoice_line_ids.filtered(
            lambda x: x.sale_line_ids == so_line_no_elaboration
        )
        self.assertEqual(
            inv_line_elaboration.name,
            "{} - {}".format(self.order.name, so_line_elaboration.name),
        )
        self.assertNotEqual(
            inv_line_no_elaboration.name,
            "{} - {}".format(self.order.name, so_line_no_elaboration.name),
        )

    def test_sale_elaboration_change_product(self):
        self.order.order_line.product_id = self.product_elaboration_A
        self.order.order_line.product_id_change()
        self.assertTrue(self.order.order_line.is_elaboration)
        self.order.order_line.product_id = self.product
        self.order.order_line.product_id_change()
        self.assertFalse(self.order.order_line.is_elaboration)
