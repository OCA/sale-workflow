# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLineInput(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Test 2"})
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

    def test_compute_name(self):
        """Test `_compute_name` computes name correctly"""
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 50.0,
                "name": "",
                "order_id": sale_order.id,
            }
        )
        line._compute_name()
        self.assertEqual(line.order_id, sale_order, "Order ID should be set correctly")
        self.assertIsNotNone(
            line.order_id.partner_id, "Partner ID should be set correctly"
        )
        self.assertEqual(
            line.order_id.partner_id,
            self.partner,
            "Order ID should be assigned correctly",
        )
