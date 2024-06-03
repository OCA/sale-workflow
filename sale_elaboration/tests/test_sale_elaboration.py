# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSaleElaboration(AccountTestInvoicingCommon):
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
        cls.order = cls._create_sale_order(
            cls, [(cls.product, 10, [cls.elaboration_a])]
        )

    def _create_sale_order(self, products_info):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        for product, qty, elaborations in products_info:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = qty
                for elaboration in elaborations:
                    line_form.elaboration_ids.add(elaboration)
        return order_form.save()

    def test_search_elaboration(self):
        elaboration = self.Elaboration.name_search("Elaboration")
        self.assertEqual(len(elaboration), 2)
        elaboration = self.Elaboration.name_search("AA")
        self.assertEqual(len(elaboration), 1)

    def test_sale_elaboration_doesnt_change(self):
        self.order.order_line.elaboration_note = "Some details"
        self.order.order_line.elaboration_ids = self.elaboration_b
        self.assertEqual(self.order.order_line.elaboration_note, "Some details")

    def test_sale_elaboration(self):
        self.order.action_confirm()
        self.order.picking_ids.move_ids.quantity_done = 10.0
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
        self.order.picking_ids.move_ids.quantity_done = 10.0
        self.order.picking_ids._action_done()
        elaboration_lines = self.order.order_line.filtered("is_elaboration")
        self.assertEqual(len(elaboration_lines), 1)
        self.assertEqual(elaboration_lines.product_uom_qty, 11.0)

    def test_invoice_elaboration(self):
        self.order = self._create_sale_order(
            [
                (self.product_elaboration_A, 1, []),
                (self.product_elaboration_B, 1, []),
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
        self.assertTrue(self.order.order_line.is_elaboration)
        self.order.order_line.product_id = self.product
        self.assertFalse(self.order.order_line.is_elaboration)

    def test_multi_elaboration_per_line(self):
        product2 = self.env["product.product"].create({"name": "product 2"})
        with Form(self.order) as order_form:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product2
                line_form.product_uom_qty = 1
                line_form.elaboration_ids.add(self.elaboration_a)
                line_form.elaboration_ids.add(self.elaboration_b)
        self.order.action_confirm()
        move_ids = self.order.picking_ids.move_ids
        move_line_a = move_ids.filtered(lambda r: r.product_id == self.product)
        move_line_a.quantity_done = 10.0
        move_line_b = move_ids.filtered(lambda r: r.product_id == product2)
        move_line_b.quantity_done = 1.0
        self.order.picking_ids._action_done()
        elaboration_lines = self.order.order_line.filtered("is_elaboration")
        self.assertEqual(len(elaboration_lines), 2)
        self.assertEqual(sum(elaboration_lines.mapped("product_uom_qty")), 12.0)

    def test_propagation_from_sale_order_to_stock_move(self):
        with Form(self.order) as order_f:
            # Edit order's line to add custom elaboration note
            with order_f.order_line.edit(0) as line_f:
                line_f.elaboration_note = "Custom note 1"
            # Add a new line with a custom elaboration note, but without elaborations
            with order_f.order_line.new() as line_f:
                line_f.product_id = self.product
                line_f.product_uom_qty = 1
                line_f.elaboration_note = "Custom note 2"
        self.order.action_confirm()
        # Check that the custom elaboration notes are propagated to the stock moves
        self.assertRecordValues(
            self.order.picking_ids.move_ids,
            [
                {
                    "product_id": self.product.id,
                    "elaboration_ids": self.elaboration_a.ids,
                    "elaboration_note": "Custom note 1",
                },
                {
                    "product_id": self.product.id,
                    "elaboration_ids": [],
                    "elaboration_note": "Custom note 2",
                },
            ],
        )
