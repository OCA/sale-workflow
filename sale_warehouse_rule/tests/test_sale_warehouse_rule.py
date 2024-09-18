# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, SavepointCase


class TestSaleWarehouseRule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.template_11 = cls.env.ref("product.product_product_11_product_template")
        cls.product_11 = cls.env.ref("product.product_product_11")
        cls.product_11b = cls.env.ref("product.product_product_11b")
        cls.template_10 = cls.env.ref("product.product_product_10_product_template")
        cls.product_10 = cls.template_10.product_variant_id
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
                "product_tmpl_id": cls.template_11.id,
                "warehouse_id": cls.warehouse0.id,
            }
        )
        cls.warehouse_rule1 = cls.env["sale.warehouse.rule"].create(
            {
                "product_tmpl_id": cls.template_11.id,
                "warehouse_id": cls.warehouse1.id,
                "product_id": cls.product_11.id,
            }
        )
        cls.warehouse_rule2 = cls.env["sale.warehouse.rule"].create(
            {"product_tmpl_id": cls.template_10.id, "warehouse_id": cls.warehouse0.id}
        )

    def _create_sale_order(self, partner, products):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        for product in products:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
        return order_form.save()

    def test_sale_line_warehouse_from_product_template_warehouse_rule(self):
        self.warehouse_rule0.write({"product_id": self.product_11b.id})
        sale = self._create_sale_order(self.partner, self.product_11 + self.product_10)
        sale.action_confirm()
        self.assertEqual(self.product_11.variant_warehouse_id, self.warehouse1)
        self.assertEqual(self.product_10.variant_warehouse_id, self.warehouse0)
        self.assertEqual(len(sale.picking_ids), 2)
        order_line_product_11 = sale.order_line.filtered(
            lambda l: l.product_id == self.product_11
        )
        order_line_product_10 = sale.order_line.filtered(
            lambda l: l.product_id == self.product_10
        )
        self.assertEqual(order_line_product_11.move_ids.warehouse_id, self.warehouse1)
        self.assertEqual(order_line_product_10.move_ids.warehouse_id, self.warehouse0)

    def test_sale_line_warehouse_from_product_warehouse_rule(self):
        self.warehouse_rule0.write({"product_id": self.product_11b.id})
        sale = self._create_sale_order(self.partner, self.product_11 + self.product_11b)
        sale.action_confirm()
        order_line_product_11 = sale.order_line.filtered(
            lambda l: l.product_id == self.product_11
        )
        order_line_product_11b = sale.order_line.filtered(
            lambda l: l.product_id == self.product_11b
        )
        self.assertEqual(order_line_product_11.move_ids.warehouse_id, self.warehouse1)
        self.assertEqual(order_line_product_11b.move_ids.warehouse_id, self.warehouse0)

    def test_sale_line_warehouse_from_attribute_values_warehouse_rule(self):
        ptav_product_11 = self.product_11.product_template_attribute_value_ids
        ptav_product_11b = self.product_11b.product_template_attribute_value_ids
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
                ],
                "product_id": False,
            }
        )
        sale = self._create_sale_order(self.partner, self.product_11 + self.product_11b)
        sale.action_confirm()
        order_line_product_11 = sale.order_line.filtered(
            lambda l: l.product_id == self.product_11
        )
        order_line_product_11b = sale.order_line.filtered(
            lambda l: l.product_id == self.product_11b
        )
        self.assertEqual(order_line_product_11.move_ids.warehouse_id, self.warehouse0)
        self.assertEqual(order_line_product_11b.move_ids.warehouse_id, self.warehouse1)

    def test_check_warehouse_rule_uniqueness_variant(self):
        with self.assertRaises(ValidationError) as m:
            self.env["sale.warehouse.rule"].create(
                {
                    "product_tmpl_id": self.template_11.id,
                    "warehouse_id": self.warehouse0.id,
                    "product_id": self.product_11.id,
                }
            )
        self.assertEqual(
            "A rule with the same product already exists.", m.exception.name
        )

    def test_check_warehouse_rule_uniqueness_template(self):
        with self.assertRaises(ValidationError) as m:
            self.env["sale.warehouse.rule"].create(
                {
                    "product_tmpl_id": self.template_10.id,
                    "warehouse_id": self.warehouse1.id,
                }
            )
        self.assertEqual(
            "Warehouse rules must be unique by template.", m.exception.name
        )
