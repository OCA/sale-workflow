# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.sale_product_set.tests.test_product_set import (
    TestProductSet,
)


class TestProductSetPackaging(TestProductSet):
    def test_packaging_qty(self):
        self.line = self.env.ref("product_set.product_set_line_computer_3")
        self.packaging = self.env["product.packaging"].create(
            {"name": "Box", "product_id": self.line.product_id.id, "qty": 10}
        )
        self.line.product_packaging_id = self.packaging.id
        self.line.product_packaging_qty = 1
        wiz = self._get_wiz()
        wiz.product_set_line_ids = self.line.ids
        wiz.add_set()
        order_line = self.so.order_line.filtered(
            lambda x: x.product_id == self.line.product_id
        )
        order_line.ensure_one()
        self.assertEqual(
            order_line.product_packaging_id, self.line.product_packaging_id
        )
        # in _get_wiz: quantity=2, meaning there are 2 sets
        self.assertEqual(order_line.product_uom_qty, self.line.quantity * 2)
