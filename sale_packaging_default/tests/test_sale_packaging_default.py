# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.tests.common import Form

from odoo.addons.product.tests.common import ProductCommon


class SalePackagingDefaultCase(ProductCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("product.group_stock_packaging")
        with Form(cls.product) as product_f:
            with product_f.packaging_ids.new() as packaging_f:
                packaging_f.name = "Dozen"
                packaging_f.sequence = 10
                packaging_f.qty = 12
                packaging_f.sales = True
            with product_f.packaging_ids.new() as packaging_f:
                packaging_f.name = "Big box"
                packaging_f.sequence = 20
                packaging_f.qty = 100
                packaging_f.sales = True
                packaging_f.sales_default = True
        cls.dozen, cls.big_box = cls.product.packaging_ids

    def test_packaging_sales_default_automation(self):
        """Sales default should be only for a packaging available for sale."""
        with Form(self.product) as product_f:
            # User creates a new packaging for the product
            with product_f.packaging_ids.new() as packaging_f:
                packaging_f.name = "Pallet"
                packaging_f.qty = 1000
                # It is not available for sale
                packaging_f.sales = False
                # So, sales_default is invisible
                with self.assertRaises(
                    AssertionError, msg="can't write on invisible field sales_default"
                ):
                    packaging_f.sales_default = True
                # But, if we make it available for sale, sales_default is visible
                packaging_f.sales = True
                packaging_f.sales_default = True
                # And, when not saleable, it is removed from default
                packaging_f.sales = False
                packaging_f.sales = True
                self.assertFalse(packaging_f.sales_default)

    def test_default_packaging_sale_order(self):
        """Check is packaging usage in sale order."""
        # Create a sale order with the product
        so_f = Form(self.env["sale.order"])
        so_f.partner_id = self.partner
        with so_f.order_line.new() as line_f:
            line_f.product_id = self.product
            # Automatically set the default packaging and the quantity
            self.assertEqual(line_f.product_packaging_id, self.big_box)
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_uom_qty, 100)
            # Change the packaging, and qtys are recalculated
            line_f.product_packaging_id = self.dozen
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_uom_qty, 12)
            # Change product qty, and packaging is recalculated
            line_f.product_uom_qty = 1200
            self.assertEqual(line_f.product_packaging_qty, 12)
            self.assertEqual(line_f.product_packaging_id, self.big_box)
            self.assertEqual(line_f.product_uom_qty, 1200)
            # I want it in dozens, so I change the packaging
            line_f.product_packaging_id = self.dozen
            self.assertEqual(line_f.product_packaging_id, self.dozen)
            self.assertEqual(line_f.product_uom_qty, 1200)
            self.assertEqual(line_f.product_packaging_qty, 100)
            # I want less dozens, so I change the packaging qty
            line_f.product_packaging_qty = 90
            self.assertEqual(line_f.product_packaging_id, self.dozen)
            self.assertEqual(line_f.product_uom_qty, 1080)
            # Change the packaging again, and qtys are recalculated
            line_f.product_packaging_id = self.big_box
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_uom_qty, 100)
            # I want more units, so I change the uom qty
            line_f.product_uom_qty = 120
            self.assertEqual(line_f.product_packaging_qty, 10)
            self.assertEqual(line_f.product_packaging_id, self.dozen)
            # If I set a uom qty without packaging, it is emptied
            line_f.product_uom_qty = 7
            self.assertFalse(line_f.product_packaging_id)
            self.assertEqual(line_f.product_packaging_qty, 0)
            self.assertEqual(line_f.product_uom_qty, 7)
            # Setting zero uom qty resets to the default packaging
            line_f.product_uom_qty = 0
            self.assertEqual(line_f.product_packaging_id, self.big_box)
            self.assertEqual(line_f.product_packaging_qty, 0)
            self.assertEqual(line_f.product_uom_qty, 0)

    def test_sale_order_product_picker_compatibility(self):
        """Emulate a call done by the product picker module and see it works.

        This test asserts support for cross-compatibility with
        `sale_order_product_picker`.
        """
        so_f = Form(
            self.env["sale.order"].with_context(
                default_product_id=self.product.id, default_price_unit=20
            )
        )
        so_f.partner_id = self.partner
        # User clicks on +1 button
        with so_f.order_line.new() as line_f:
            self.assertEqual(line_f.product_uom_qty, 1)
            self.assertFalse(line_f.product_packaging_id)
