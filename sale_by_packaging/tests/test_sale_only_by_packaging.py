# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, SavepointCase
from odoo.tools import mute_logger


class TestSaleProductByPackagingOnly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.SaleOrder = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.precision = cls.env["decimal.precision"].precision_get("Product Price")

    def test_write_auto_fill_packaging(self):
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
            }
        )
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.write({"product_uom_qty": 3.0})
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        self.product.write({"sell_only_by_packaging": True})
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.write({"product_uom_qty": self.packaging.qty * 2})
        self.assertTrue(order_line.product_packaging)
        self.assertTrue(order_line.product_packaging_qty)
        self.assertEqual(order_line.product_packaging.name, "Test packaging")
        self.assertEqual(order_line.product_packaging_qty, 2)

        packaging_10 = self.env["product.packaging"].create(
            {"name": "Test packaging 10", "product_id": self.product.id, "qty": 15.0}
        )
        order_line.write({"product_uom_qty": packaging_10.qty * 2})
        self.assertEqual(order_line.product_packaging.name, "Test packaging 10")

        with self.assertRaises(ValidationError):
            order_line.write({"product_packaging": False})

    def test_create_auto_fill_packaging(self):
        """Check when the packaging should be set automatically on the line
        """
        # sell_only_by_packaging is default False
        order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": self.packaging.qty * 2,
            }
        )
        self.assertFalse(order_line_1.product_packaging)
        self.assertFalse(order_line_1.product_packaging_qty)

        self.product.write({"sell_only_by_packaging": True})
        order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": self.packaging.qty * 2,
            }
        )
        self.assertTrue(order_line_1.product_packaging)
        self.assertTrue(order_line_1.product_packaging_qty)
        self.assertEqual(order_line_1.product_packaging.name, "Test packaging")
        self.assertEqual(order_line_1.product_packaging_qty, 2)

        with self.assertRaises(ValidationError):
            self.env["sale.order.line"].create(
                {
                    "order_id": self.order.id,
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 2,
                }
            )

    @mute_logger("odoo.tests.common.onchange")
    def test_convert_packaging_qty(self):
        """
        Test if the function _convert_packaging_qty is correctly applied
        during SO line create/edit and if qties are corrects.
        :return:
        """
        self.product.sell_only_by_packaging = True
        packaging = fields.first(self.product.packaging_ids)
        # For this step, the qty is not forced on the packaging so nothing
        # should happens if the qty doesn't match with packaging multiple.
        with Form(self.SaleOrder) as sale_order:
            sale_order.partner_id = self.partner
            with sale_order.order_line.new() as so_line:
                so_line.product_id = self.product
                so_line.product_packaging = packaging
                so_line.product_uom_qty = 12
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 12, places=self.precision
                )
                so_line.product_uom_qty = 10
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 10, places=self.precision
                )
                so_line.product_uom_qty = 36
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 36, places=self.precision
                )
                so_line.product_uom_qty = 10
                so_line.product_packaging = packaging
        # Now force the qty on the packaging
        packaging.force_sale_qty = True
        with Form(self.SaleOrder) as sale_order:
            sale_order.partner_id = self.partner
            with sale_order.order_line.new() as so_line:
                so_line.product_id = self.product
                so_line.product_packaging = packaging
                so_line.product_uom_qty = 12
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 15, places=self.precision
                )
                so_line.product_uom_qty = 10
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 10, places=self.precision
                )
                so_line.product_uom_qty = 8
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 10, places=self.precision
                )
                so_line.product_uom_qty = 11
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 15, places=self.precision
                )
                so_line.product_uom_qty = 208
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 210, places=self.precision
                )
                so_line.product_uom_qty = 209.98
                self.assertAlmostEqual(
                    so_line.product_uom_qty, 210, places=self.precision
                )

    def test_packaging_qty_non_zero(self):
        """ Check product packaging quantity.

        The packaging quantity can not be zero.
        """
        self.product.write({"sell_only_by_packaging": True})
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,  # 2 packs
            }
        )
        with self.assertRaises(ValidationError):
            order_line.write({"product_uom_qty": 3, "product_packaging_qty": 0})

    def test_onchange_qty_is_not_pack_multiple(self):
        """ Check package when qantity is not a multiple of package quantity.

        When the uom quantity is changed for a value not a multpile of a
        possible package an error is raised.
        """
        self.product.write({"sell_only_by_packaging": True})
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,  # 2 packs
            }
        )
        with self.assertRaises(ValidationError):
            order_line.write({"product_uom_qty": 3})
