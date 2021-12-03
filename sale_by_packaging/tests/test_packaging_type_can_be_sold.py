# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError

from .common import Common


class TestPackagingTypeCanBeSold(Common):
    @classmethod
    def setUpClassSaleOrder(cls):
        super().setUpClassSaleOrder()
        cls.order_line.product_uom_qty = 3.0

    def test_packaging_type_can_be_sold(self):
        self.order_line.write({"product_packaging": self.packaging_tu.id})
        with self.assertRaises(ValidationError):
            self.order_line.write(
                {"product_packaging": self.packaging_cannot_be_sold.id}
            )
            onchange_res = self.order_line._onchange_product_packaging()
            self.assertIn("warning", onchange_res)

    def test_product_packaging_can_be_sold(self):
        """Check that a product.packaging can be independently set as can be sold."""
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
        self.sellable_packagings.unlink()
        self.packaging_cannot_be_sold.packaging_type_id = self.packaging_type_tu
        self.packaging_cannot_be_sold.packaging_type_id = (
            self.packaging_type_cannot_be_sold
        )
        self.assertEqual(self.packaging_cannot_be_sold.can_be_sold, False)
        # Changing the can_be_sold on the packaging_type does not update the packaging
        self.packaging_type_cannot_be_sold.can_be_sold = True
        self.assertEqual(self.packaging_cannot_be_sold.can_be_sold, False)
