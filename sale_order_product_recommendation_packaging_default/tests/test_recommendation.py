# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from freezegun import freeze_time

from odoo.fields import Command
from odoo.tests.common import Form

from odoo.addons.sale_order_product_recommendation.tests import (
    test_recommendation_common,
)


@freeze_time("2021-10-02 15:30:00", tick=True)
class PackagingRecommendationCase(test_recommendation_common.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("product.group_stock_packaging")
        # Product 1 has 3 packagings
        cls.prod_1_dozen, cls.prod_1_box, cls.prod_1_pallet = cls.env[
            "product.packaging"
        ].create(
            [
                # By default, it is sold in dozens
                {
                    "name": "Dozen",
                    "product_id": cls.prod_1.id,
                    "qty": 12,
                    "sales": True,
                    "sequence": 1,
                },
                # It can be also sold in big boxes
                {
                    "name": "Box",
                    "product_id": cls.prod_1.id,
                    "qty": 120,
                    "sales": True,
                    "sequence": 10,
                },
                # We can store it in pallets, but that's not used in sales
                {
                    "name": "Pallet",
                    "product_id": cls.prod_1.id,
                    "qty": 1440,
                    "sales": False,
                    "sequence": 30,
                },
            ]
        )
        # Product 2 has only one sale packaging, used by default
        cls.prod_2_dozen = cls.env["product.packaging"].create(
            {
                "name": "Dozen",
                "product_id": cls.prod_2.id,
                "qty": 12,
                "sales": True,
            }
        )

    def test_defaults(self):
        """Test default values."""
        wiz = self.wizard()
        self.assertRecordValues(
            wiz.line_ids,
            [
                {
                    "product_id": self.prod_2.id,
                    "product_packaging_id": self.prod_2_dozen.id,
                    "product_packaging_qty": 0,
                    "units_included": 0,
                },
                {
                    "product_id": self.prod_3.id,
                    "product_packaging_id": False,
                    "product_packaging_qty": 0,
                    "units_included": 0,
                },
                {
                    "product_id": self.prod_1.id,
                    "product_packaging_id": self.prod_1_dozen.id,
                    "product_packaging_qty": 0,
                    "units_included": 0,
                },
            ],
        )

    def test_computes(self):
        """User makes changes in lines, and they behave as expected."""
        wiz_f = Form(self.wizard())
        with wiz_f.line_ids.edit(0) as line:
            # Setting to zero works as expected
            line.product_packaging_qty = 0
            self.assertEqual(line.product_packaging_id, self.prod_2_dozen)
            self.assertEqual(line.product_packaging_qty, 0)
            self.assertEqual(line.units_included, 0)
            # I want to sell 2 dozens of product 2
            self.assertEqual(line.product_packaging_id, self.prod_2_dozen)
            self.assertEqual(line.product_packaging_qty, 0)
            self.assertEqual(line.units_included, 0)
            line.product_packaging_qty = 2
            self.assertEqual(line.units_included, 24)
        with wiz_f.line_ids.edit(1) as line:
            # Product 3 is sold by units
            self.assertFalse(line.product_packaging_id)
            self.assertEqual(line.product_packaging_qty, 0)
            self.assertEqual(line.units_included, 0)
            # I want to sell 100 units of product 3
            line.units_included = 100
            self.assertFalse(line.product_packaging_id)
            self.assertEqual(line.product_packaging_qty, 0)
            self.assertEqual(line.units_included, 100)
        with wiz_f.line_ids.edit(2) as line:
            self.assertEqual(line.product_packaging_id, self.prod_1_dozen)
            # I cannot sell product 1 in pallets
            line.product_packaging_id = self.prod_1_pallet
            # I want to sell a box of product 1
            line.units_included = 120
            self.assertEqual(line.product_packaging_id, self.prod_1_box)
            self.assertEqual(line.product_packaging_qty, 1)
            # I want to sell the same amount of units, but in dozens
            line.product_packaging_id = self.prod_1_dozen
            self.assertEqual(line.product_packaging_qty, 1)
            self.assertEqual(line.units_included, 12)
            line.product_packaging_qty = 10
            self.assertEqual(line.product_packaging_id, self.prod_1_dozen)
            self.assertEqual(line.product_packaging_qty, 10)
            self.assertEqual(line.units_included, 120)
        # After saving, the SO has the expected values
        wiz = wiz_f.save()
        wiz.action_accept()
        self.assertRecordValues(
            self.new_so.order_line,
            [
                {
                    "product_id": self.prod_2.id,
                    "product_packaging_id": self.prod_2_dozen.id,
                    "product_packaging_qty": 2,
                    "product_uom_qty": 24,
                },
                {
                    "product_id": self.prod_3.id,
                    "product_packaging_id": False,
                    "product_packaging_qty": 0,
                    "product_uom_qty": 100,
                },
                {
                    "product_id": self.prod_1.id,
                    "product_packaging_id": self.prod_1_dozen.id,
                    "product_packaging_qty": 10,
                    "product_uom_qty": 120,
                },
            ],
        )

    def test_preexisting_product(self):
        self.new_so.order_line = [
            Command.create(
                {
                    "product_id": self.prod_1.id,
                    "product_uom_qty": 12,
                    "qty_delivered_method": "manual",
                }
            )
        ]
        wiz_f = Form(self.wizard())
        with wiz_f.line_ids.edit(1) as line:
            self.assertEqual(line.product_id, self.prod_1)
            self.assertEqual(line.product_packaging_id, self.prod_1_dozen)
            self.assertEqual(line.product_packaging_qty, 1)
            self.assertEqual(line.units_included, 12)
            line.product_packaging_qty = 10
            self.assertEqual(line.product_packaging_id, self.prod_1_dozen)
            self.assertEqual(line.product_packaging_qty, 10)
            self.assertEqual(line.units_included, 120)
        wiz = wiz_f.save()
        wiz.action_accept()
        self.assertRecordValues(
            self.new_so.order_line,
            [
                {
                    "product_id": self.prod_1.id,
                    "product_packaging_id": self.prod_1_dozen.id,
                    "product_packaging_qty": 10,
                    "product_uom_qty": 120,
                },
            ],
        )

    def test_no_packaging_user(self):
        self.env.user.groups_id -= self.env.ref("product.group_stock_packaging")
        wiz_f = Form(self.wizard())
        with wiz_f.line_ids.edit(2) as line:
            self.assertEqual(line.product_id, self.prod_1)
            line.units_included = 12
        wizard = wiz_f.save()
        wizard.action_accept()
        self.assertRecordValues(
            self.new_so.order_line,
            [
                {
                    "product_id": self.prod_1.id,
                    "product_uom_qty": 12,
                },
            ],
        )
