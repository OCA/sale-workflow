# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestSaleOrderLineInput(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.partner_2 = cls.env.ref("base.res_partner_2")
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def test_sale_order_create_and_show(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        sale_order = sale_order_form.save()
        line_form = Form(
            self.env["sale.order.line"],
            view="sale_order_line_input.view_sales_order_line_input_tree",
        )
        line_form.order_id = sale_order
        line_form.product_id = self.product
        line_form.price_unit = 190.50
        line_form.product_uom = self.uom_unit
        line_form.product_uom_qty = 8.0
        line_form.name = "Test line description"
        line = line_form.save()
        self.assertTrue(line.order_id)
        action_dict = line.action_sale_order_form()
        self.assertEqual(action_dict["res_id"], line.order_id.id)
        self.assertEqual(action_dict["res_model"], "sale.order")
        new_sale_order_line = self.env["sale.order.line"].new(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.uom_unit.id,
                "name": "New Test Sale Order Line",
            }
        )
        new_sale_order_line.order_partner_id = self.partner_2
        new_sale_order_line._onchange_order_partner_id()
        order_vals = new_sale_order_line._convert_to_write(new_sale_order_line._cache)
        new_sale_order_line = self.env["sale.order.line"].create(order_vals)
        self.assertIsNotNone(new_sale_order_line.order_id)
        self.assertEqual(new_sale_order_line.order_id.partner_id, self.partner_2)
        existing_order_id = new_sale_order_line.order_id.id
        new_sale_order_line._onchange_order_partner_id()
        self.assertEqual(new_sale_order_line.order_id.id, existing_order_id)
        self.assertEqual(new_sale_order_line.order_id.partner_id, self.partner_2)
