# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo.exceptions import ValidationError
from odoo.tests import Form, SavepointCase


class TestSaleProductByPackagingOnly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def test_onchange_qty_is_pack_multiple(self):
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
            }
        )
        onchange_logger = logging.getLogger("odoo.tests.common.onchange")
        self.product.write({"sell_only_by_packaging": False})
        with Form(order_line.order_id) as sale_form:
            line_form = sale_form.order_line.edit(0)
            with self.assertLogs(onchange_logger, level="WARN") as logs:
                line_form.product_uom_qty = 1
                # no check
                self.assertFalse(logs.output)
                # this is a workaround for the lack of an "assertNoLogs"
                # method, that should be added at some point:
                # https://bugs.python.org/issue39385
                # assertLogs fails if no logs is emitted
                onchange_logger.warning("no warning in onchange")

            self.product.write({"sell_only_by_packaging": True})

            # form report "warnings" in the "onchange" logger
            with self.assertLogs(onchange_logger, level="WARN") as logs:
                line_form.product_uom_qty = 1
                self.assertIn(
                    "WARNING:odoo.tests.common.onchange:"
                    "Product quantity cannot be packed "
                    "For the product Pedal Bin\n"
                    "The quantity 1.0 is not the multiple"
                    " of any packaging.\n"
                    "Please add a packaging.",
                    logs.output,
                )

            with self.assertLogs(onchange_logger, level="WARN") as logs:
                line_form.product_id = self.product
                # should set the packaging, which sets the product_uom_qty
                self.assertEqual(line_form.product_packaging, self.packaging)
                self.assertEqual(line_form.product_uom_qty, self.packaging.qty)
                self.assertFalse(logs.output)
                # see above why it's there
                onchange_logger.warning("no warning in onchange")

            with self.assertLogs(onchange_logger, level="WARN") as logs:
                line_form.product_uom_qty = self.packaging.qty * 2
                # should set the packaging, which sets the product_uom_qty
                self.assertEqual(line_form.product_packaging, self.packaging)
                self.assertEqual(line_form.product_uom_qty, 10.0)
                self.assertFalse(logs.output)
                # see above why it's there
                onchange_logger.warning("no warning in onchange")

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
