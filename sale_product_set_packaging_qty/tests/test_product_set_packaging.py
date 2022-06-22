# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import exceptions
from odoo.tests import common


class TestProductSetPackaging(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line = cls.env.ref("sale_product_set.product_set_line_computer_3")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Box", "product_id": cls.line.product_id.id, "qty": 10}
        )

    def test_with_packaging(self):
        line = self.line
        line.quantity = 50
        line.product_packaging_id = self.packaging
        # 50 units of packages with 10 units each means 5 packages
        self.assertEqual(line.product_packaging_qty, 5)

    def test_write_packaging_qty(self):
        line = self.line
        line.product_packaging_id = self.packaging
        line.product_packaging_qty = 8
        # 8 packages with 10 units each means 80 units
        self.assertEqual(line.quantity, 80)

    def test_error_write_qty_but_no_packaging(self):
        line = self.line
        with self.assertRaises(exceptions.UserError):
            line.product_packaging_qty = 10

    def test_error_write_qty_but_packaging_zero(self):
        line = self.line
        line.product_packaging_id = self.packaging
        self.packaging.qty = 0
        with self.assertRaises(exceptions.UserError):
            line.product_packaging_qty = 10
