# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields
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
                packaging_f.qty = 12
                packaging_f.sales = True
                packaging_f.sequence = 20
            with product_f.packaging_ids.new() as packaging_f:
                packaging_f.name = "Big box"
                packaging_f.qty = 100
                packaging_f.sales = True
                packaging_f.sequence = 10  # This is the default one
        cls.big_box, cls.dozen = cls.product.packaging_ids
        assert cls.dozen.name == "Dozen"
        assert cls.big_box.name == "Big box"
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "consu",
                "packaging_ids": [
                    fields.Command.create(
                        {
                            "name": "3-pack",
                            "qty": 3,
                            "sales": True,
                            "sequence": 10,
                        }
                    ),
                ],
            }
        )
        cls.p2_three_pack = cls.product2.packaging_ids[0]
        assert cls.p2_three_pack.name == "3-pack"

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

    def test_product_change(self):
        """Set one product, alter qtys, change product, qtys are reset."""
        so_f = Form(self.env["sale.order"])
        so_f.partner_id = self.partner
        with so_f.order_line.new() as line_f:
            line_f.product_id = self.product
            self.assertEqual(line_f.product_packaging_id, self.big_box)
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_uom_qty, 100)
            line_f.product_uom_qty = 120
            self.assertEqual(line_f.product_packaging_id, self.dozen)
            self.assertEqual(line_f.product_packaging_qty, 10)
            self.assertEqual(line_f.product_uom_qty, 120)
            line_f.product_id = self.product2
            self.assertEqual(line_f.product_packaging_id, self.p2_three_pack)
            self.assertEqual(line_f.product_packaging_qty, 10)
            self.assertEqual(line_f.product_uom_qty, 30)
