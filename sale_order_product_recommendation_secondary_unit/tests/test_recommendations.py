# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.sale_order_product_recommendation.tests import (
    test_recommendation_common,
)


class RecommendationCaseTests(test_recommendation_common.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.prod_1.write(
            {
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Pack",
                            "product_tmpl_id": cls.prod_1.product_tmpl_id.id,
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 10,
                        },
                    )
                ]
            }
        )
        cls.secondary_unit_p1 = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.prod_1.product_tmpl_id.id)]
        )
        cls.prod_1.sale_secondary_uom_id = cls.secondary_unit_p1
        cls.prod_2.write(
            {
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Pack",
                            "product_tmpl_id": cls.prod_2.product_tmpl_id.id,
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 24,
                        },
                    )
                ]
            }
        )
        cls.secondary_unit_p2 = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.prod_2.product_tmpl_id.id)]
        )

    def test_recommendations_secondary_unit(self):
        """Tests defaults and factor functions"""
        wizard = self.wizard()
        self.assertEqual(len(wizard.line_ids), 3)
        # Product 1 has a default secondary unit
        wl_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        self.assertEqual(wl_prod1.secondary_uom_id, self.secondary_unit_p1)
        wl_prod1.units_included = 25
        wl_prod1._onchange_units_included_sale_order_secondary_unit()
        self.assertAlmostEqual(wl_prod1.secondary_uom_qty, 2.5)
        wl_prod1.secondary_uom_qty = 3
        wl_prod1._onchange_secondary_uom()
        self.assertAlmostEqual(wl_prod1.units_included, 30)
        # Product 2 has a secondary units, but no default ones
        wl_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertFalse(wl_prod2.secondary_uom_id)
        # Product 3 has no secondary units
        wl_prod3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertFalse(wl_prod3.secondary_uom_id)
        wl_prod3._onchange_secondary_uom()
        wl_prod3._onchange_units_included_sale_order_secondary_unit()
        self.assertFalse(wl_prod3.secondary_uom_id)

    def test_transfer_of_secondary_unit(self):
        """Products get transferred to SO with their secondary units"""
        wizard = self.wizard()
        wl_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        wl_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        wl_prod1.secondary_uom_qty = 2  # 20 units
        wl_prod1._onchange_secondary_uom()
        wl_prod2.secondary_uom_id = self.secondary_unit_p2
        wl_prod2.secondary_uom_qty = 2  # 48 units
        wl_prod2._onchange_secondary_uom()
        wizard.action_accept()
        self.assertEqual(len(self.new_so.order_line), 2)
        sl_p1 = self.new_so.order_line.filtered(lambda x: x.product_id == self.prod_1)
        self.assertEqual(sl_p1.secondary_uom_id, self.secondary_unit_p1)
        self.assertEqual(sl_p1.secondary_uom_qty, 2)
        self.assertEqual(sl_p1.product_uom_qty, 20)
        sl_p2 = self.new_so.order_line.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(sl_p2.secondary_uom_id, self.secondary_unit_p2)
        self.assertEqual(sl_p2.secondary_uom_qty, 2)
        self.assertEqual(sl_p2.product_uom_qty, 48)
        # Update the quantities
        wizard = self.wizard()
        wl_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        wl_prod1.secondary_uom_qty = 1  # 10 units
        wl_prod1._onchange_secondary_uom()
        wizard.action_accept()
        sl_p1 = self.new_so.order_line.filtered(lambda x: x.product_id == self.prod_1)
        self.assertEqual(sl_p1.secondary_uom_qty, 1)
        self.assertEqual(sl_p1.product_uom_qty, 10)
