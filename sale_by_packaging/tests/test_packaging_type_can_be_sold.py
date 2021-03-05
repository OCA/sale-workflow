# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestPackagingTypeCanBeSold(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging_type_can_be_sold = cls.env["product.packaging.type"].create(
            {"name": "Can be sold", "code": "CBS", "sequence": 20}
        )
        cls.packaging_type_cannot_be_sold = cls.env["product.packaging.type"].create(
            {
                "name": "Can not be sold",
                "code": "CNBS",
                "sequence": 30,
                "can_be_sold": False,
            }
        )
        cls.packaging_can_be_sold = cls.env["product.packaging"].create(
            {
                "name": "Test packaging can be sold",
                "product_id": cls.product.id,
                "qty": 5.0,
                "packaging_type_id": cls.packaging_type_can_be_sold.id,
            }
        )
        cls.packaging_cannot_be_sold = cls.env["product.packaging"].create(
            {
                "name": "Test packaging cannot be sold",
                "product_id": cls.product.id,
                "qty": 10.0,
                "packaging_type_id": cls.packaging_type_cannot_be_sold.id,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 3.0,
            }
        )

    def test_packaging_type_can_be_sold(self):
        self.order_line.write({"product_packaging": self.packaging_can_be_sold.id})
        with self.assertRaises(ValidationError):
            self.order_line.write(
                {"product_packaging": self.packaging_cannot_be_sold.id}
            )
            onchange_res = self.order_line._onchange_product_packaging()
            self.assertIn("warning", onchange_res)

    def test_product_packaging_can_be_sold(self):
        """Check that a product.packaging can be independently set as can be sold.
        """
        exception_msg = (
            "Packaging Test packaging cannot be sold on product {} must be set "
            "as 'Can be sold' in order to be used on a sale order."
        ).format(self.product.name)
        with self.assertRaisesRegex(ValidationError, exception_msg):
            self.order_line.write(
                {"product_packaging": self.packaging_cannot_be_sold.id}
            )
        # Packaging can be sold even if the packaging type does not allows it
        self.packaging_cannot_be_sold.can_be_sold = True
        self.order_line.write({"product_packaging": self.packaging_cannot_be_sold.id})
        # Changing the packaging type on product.packaging updates can_be_sold
        self.packaging_can_be_sold.unlink()
        self.packaging_cannot_be_sold.packaging_type_id = (
            self.packaging_type_can_be_sold
        )
        self.packaging_cannot_be_sold.packaging_type_id = (
            self.packaging_type_cannot_be_sold
        )
        self.assertEqual(self.packaging_cannot_be_sold.can_be_sold, False)
        # Changing the can_be_sold on the packaging_type does not update the packaging
        self.packaging_type_cannot_be_sold.can_be_sold = True
        self.assertEqual(self.packaging_cannot_be_sold.can_be_sold, False)
