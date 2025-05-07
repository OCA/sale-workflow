# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestDiscountDisplay(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product TEST", "type": "consu"}
        )
        cls.so = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.so_line = cls.env["sale.order.line"].create(
            {"order_id": cls.so.id, "product_id": cls.product.id, "price_unit": 30.75}
        )

    def test_sale_discount_value(self):
        self.so_line.discount = 10
        self.assertAlmostEqual(self.so_line.price_total_no_discount, 35.36)
        self.assertAlmostEqual(self.so_line.discount_total, 3.53)
        self.assertAlmostEqual(self.so.discount_total, 3.53)
        self.assertAlmostEqual(self.so.price_total_no_discount, 35.36)

    def test_sale_without_discount_value(self):
        self.assertEqual(self.so_line.price_total_no_discount, self.so_line.price_total)

    def test_unlink_after_compute_discount_total(self):
        # Regression test: compute_discount_total must not write unchanged values,
        # otherwise unlink raises a cache error when flushing triggers
        # recomputation on records being deleted.
        self.so_line.discount = 10
        self.assertAlmostEqual(self.so_line.price_total_no_discount, 35.36)
        so_id = self.so.id
        self.so.unlink()
        # Check that the sale order is deleted
        self.assertFalse(self.env["sale.order"].browse(so_id).exists())
