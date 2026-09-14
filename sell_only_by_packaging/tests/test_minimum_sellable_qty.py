# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import TransactionCase


class TestMinimumSellableQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging_level_1 = cls.env["product.packaging.level"].create(
            {"name": "Packaging level 1", "code": "PL1", "sequence": 1}
        )
        cls.packaging_level_2 = cls.env["product.packaging.level"].create(
            {"name": "Packaging level 1", "code": "PL2", "sequence": 2}
        )
        cls.packaging_level_3 = cls.env["product.packaging.level"].create(
            {"name": "Packaging level 3", "code": "PL3", "sequence": 3}
        )
        cls.packaging1 = cls.env["product.packaging"].create(
            {
                "name": "Packaging of five",
                "product_id": cls.product.id,
                "qty": 5.0,
                "packaging_level_id": cls.packaging_level_1.id,
            }
        )
        cls.packaging2 = cls.env["product.packaging"].create(
            {
                "name": "Packing of 3",
                "product_id": cls.product.id,
                "qty": 3.0,
                "packaging_level_id": cls.packaging_level_2.id,
            }
        )

    def test_min_sellable_qty(self):
        """Check the computation of the minimum sellable quantity."""
        self.product.product_tmpl_id.sell_only_by_packaging = False
        self.assertEqual(self.product.min_sellable_qty, 0)
        self.product.product_tmpl_id.sell_only_by_packaging = True
        self.assertEqual(self.product.min_sellable_qty, 3)
        self.assertEqual(self.product.product_tmpl_id.min_sellable_qty, 3)
        self.packaging2.sales = False
        self.assertEqual(self.product.min_sellable_qty, 5)
        self.assertEqual(self.product.product_tmpl_id.min_sellable_qty, 5)
        self.packaging3 = self.env["product.packaging"].create(
            {
                "name": "Packing of 2",
                "product_id": self.product.id,
                "qty": 2.0,
                "packaging_level_id": self.packaging_level_3.id,
            }
        )
        self.assertEqual(self.product.min_sellable_qty, 2)
        self.assertEqual(self.product.product_tmpl_id.min_sellable_qty, 2)
