# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestPackagingCanBeSold(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging_can_be_sold = cls.env["product.packaging"].create(
            {
                "name": "Test packaging can be sold",
                "product_id": cls.product.id,
                "qty": 5.0,
            }
        )
        cls.packaging_cannot_be_sold = cls.env["product.packaging"].create(
            {
                "name": "Test packaging cannot be sold",
                "product_id": cls.product.id,
                "qty": 10.0,
                "can_be_sold": False,
            }
        )

    def test_packaging_can_be_sold(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 3.0,
            }
        )
        order_line.write({"product_packaging": self.packaging_can_be_sold.id})
        with self.assertRaises(ValidationError):
            order_line.write({"product_packaging": self.packaging_cannot_be_sold.id})
            onchange_res = order_line._onchange_product_packaging()
            self.assertIn("warning", onchange_res)
