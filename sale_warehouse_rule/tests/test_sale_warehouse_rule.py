# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestSaleWarehouseRule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_template_11 = cls.env.ref(
            "product.product_product_11_product_template"
        )
        cls.product_product_11 = cls.env.ref("product.product_product_11")
        cls.product_product_11b = cls.env.ref("product.product_product_11b")
        cls.warehouse0 = cls.env.ref("stock.warehouse0")
        cls.warehouse1 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 1",
                "code": "WHONE",
                "partner_id": cls.env.ref("base.res_partner_2").id,
                "company_id": cls.warehouse0.company_id.id,
            }
        )
        cls.warehouse_rule0 = cls.env["sale.warehouse.rule"].create(
            {
                "product_tmpl_id": cls.product_template_11.id,
                "warehouse_id": cls.warehouse0.id,
            }
        )
        cls.warehouse_rule1 = cls.env["sale.warehouse.rule"].create(
            {
                "product_tmpl_id": cls.product_template_11.id,
                "warehouse_id": cls.warehouse1.id,
            }
        )

    def test_sale_line_warehouse_from_product_warehouse_rule(self):
        self.warehouse_rule0.write({"product_id": self.product_product_11.id})
        self.warehouse_rule1.write({"product_id": self.product_product_11b.id})
        sale = self._create_sale_order(
            self.partner, self.product_product_11 + self.product_product_11b
        )
        sale.action_confirm()
        product_product_11 = self.product_product_11
        product_product_11b = self.product_product_11b
        order_line_product_11 = sale.order_line.filtered(
            lambda l: l.product_id == product_product_11
        )
        order_line_product_11b = sale.order_line.filtered(
            lambda l: l.product_id == product_product_11b
        )
        self.assertEqual(
            order_line_product_11.move_ids.mapped("warehouse_id"), self.warehouse0
        )
        self.assertEqual(
            order_line_product_11b.move_ids.mapped("warehouse_id"), self.warehouse1
        )

    def test_sale_line_warehouse_from_attribute_values_warehouse_rule(self):
        ptav_product_11 = self.product_product_11.product_template_attribute_value_ids
        ptav_product_11b = self.product_product_11b.product_template_attribute_value_ids
        self.warehouse_rule0.write(
            {
                "attribute_value_ids": [
                    (6, 0, ptav_product_11.product_attribute_value_id.ids)
                ]
            }
        )
        self.warehouse_rule1.write(
            {
                "attribute_value_ids": [
                    (6, 0, ptav_product_11b.product_attribute_value_id.ids)
                ]
            }
        )
        sale = self._create_sale_order(
            self.partner, self.product_product_11 + self.product_product_11b
        )
        sale.action_confirm()
        product_product_11 = self.product_product_11
        product_product_11b = self.product_product_11b
        order_line_product_11 = sale.order_line.filtered(
            lambda l: l.product_id == product_product_11
        )
        order_line_product_11b = sale.order_line.filtered(
            lambda l: l.product_id == product_product_11b
        )
        self.assertEqual(
            order_line_product_11.move_ids.mapped("warehouse_id"), self.warehouse0
        )
        self.assertEqual(
            order_line_product_11b.move_ids.mapped("warehouse_id"), self.warehouse1
        )

    def _create_sale_order(self, partner, products):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        for product in products:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
        return order_form.save()
