# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleOrderLineInput(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service",}
        )

    def test_sale_order_create_and_show(self):
        line = self.env["sale.order.line"].create(
            {
                "order_partner_id": self.partner.id,
                "product_id": self.product.id,
                "price_unit": 190.50,
                "product_uom": self.ref("product.decimal_product_uom"),
                "product_uom_qty": 8.0,
                "name": "Test line description",
            }
        )
        self.assertTrue(line.order_id)
        action_dict = line.action_sale_order_form()
        self.assertEquals(action_dict["res_id"], line.order_id.id)
        self.assertEquals(action_dict["res_model"], "sale.order")
