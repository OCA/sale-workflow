# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import UserError
from odoo.tests import SavepointCase


class TestSaleOrderLinePackagingQty(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.product_no_pckg = cls.env.ref("product.product_product_10")

    def test_product_packaging_qty(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 3.0,
            }
        )
        order_line.write({"product_packaging": self.packaging})
        # This is what actually happened when user adds so line
        order_line._onchange_product_uom_qty()
        order_line._compute_product_packaging_qty()
        order_line._onchange_product_packaging()
        order_line._onchange_product_packaging_qty()
        self.assertEqual(order_line.product_uom_qty, 5.0)
        self.assertEqual(order_line.product_packaging_qty, 1.0)

        order_line.write({"product_packaging_qty": 3.0})
        order_line._onchange_product_packaging_qty()
        self.assertEqual(order_line.product_uom_qty, 15.0)

        order_line.write({"product_uom_qty": 9.0})
        self.assertEqual(order_line.product_packaging_qty, 0.0)
        order_line.write({"product_uom_qty": 15.0})

        dozen = self.env.ref("uom.product_uom_dozen")
        order_line.product_uom = dozen
        order_line._compute_product_packaging_qty()
        self.assertEqual(order_line.product_uom_qty, 180.0)
        self.assertEqual(order_line.product_uom, self.product.uom_id)

        self.packaging.qty = 0
        with self.assertRaises(UserError):
            order_line.write({"product_packaging_qty": 0.0})

        order_line.product_packaging = False
        order_line._onchange_product_packaging()
        self.assertEqual(order_line.product_packaging_qty, 0.0)

    def test_product_packaging_qty_wo_packaging(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product_no_pckg.id,
                "product_uom": self.product_no_pckg.uom_id.id,
                "product_uom_qty": 3.0,
            }
        )
        order_line._compute_product_packaging_qty()
        self.assertEqual(order_line.product_uom_qty, 3.0)
        self.assertEqual(order_line.product_packaging_qty, 0.0)
        with self.assertRaises(UserError):
            order_line.write({"product_packaging_qty": 3.0})

    def test_product_packaging_qty_from_external(self):
        """The previous ones have product_uom_qty of 3, which is less than and
        not divisible by packaging qty of 5. This test is to increase coverage
        for the case that product_uom_qty of 15 is divisible by 5.
        """
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 15.0,
            }
        )
        order_line.write({"product_packaging": self.packaging})
        order_line._onchange_product_packaging()
        self.assertEqual(order_line.product_packaging_qty, 3.0)
