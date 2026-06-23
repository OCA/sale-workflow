# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from freezegun import freeze_time

from odoo.fields import Command

from odoo.addons.sale_order_product_recommendation.tests import (
    test_recommendation_common,
)


@freeze_time("2021-10-02 15:30:00")
class RecommendationCaseTests(test_recommendation_common.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product 2 was sold with 2 small elaborations
        o1p2line = cls.order1.order_line[1]
        assert o1p2line.product_id == cls.prod_2
        cls.prod_small_elab = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Small elaboration",
                    "is_elaboration": True,
                    "type": "service",
                    "list_price": 1,
                }
            )
        )
        cls.elab_1, cls.elab_2 = (
            cls.env["product.elaboration"]
            .sudo()
            .create(
                [
                    {
                        "product_id": cls.prod_small_elab.id,
                        "name": "Elaboration 1",
                    },
                    {
                        "product_id": cls.prod_small_elab.id,
                        "name": "Elaboration 2",
                    },
                ]
            )
        )
        o1p2line.elaboration_ids = cls.elab_1 | cls.elab_2
        # An older order had only elaboration 1, but the newest one will be used
        assert cls.order2.order_line.product_id == cls.prod_2
        cls.order2.order_line.elaboration_ids = cls.elab_1

    def test_recommendations_from_last_sale(self):
        wizard = self.wizard()
        # Find line for product 1
        wiz_line = wizard.line_ids.filtered_domain(
            [("product_id", "=", self.prod_2.id)]
        )
        wiz_line.ensure_one()
        self.assertEqual(wiz_line.elaboration_ids, self.elab_1 | self.elab_2)
        self.assertFalse(wiz_line.elaboration_note)
        wiz_line.elaboration_note = "Elaborations 1 and 2"
        # Include 1 of those
        wiz_line.units_included = 1
        wizard.action_accept()
        # Check elaborations got included
        self.assertEqual(len(self.new_so.order_line), 1)
        self.assertEqual(self.new_so.order_line.product_id, self.prod_2)
        self.assertEqual(self.new_so.order_line.product_uom_qty, 1)
        self.assertEqual(
            self.new_so.order_line.elaboration_ids,
            self.elab_1 | self.elab_2,
        )
        self.assertEqual(
            self.new_so.order_line.elaboration_note, "Elaborations 1 and 2"
        )

    def test_recommendations_from_current_sale(self):
        self.new_so.order_line = [
            Command.create(
                {
                    "product_id": self.prod_2.id,
                    "product_uom_qty": 1,
                    "elaboration_ids": self.elab_2,
                }
            )
        ]
        self.assertEqual(len(self.new_so.order_line), 1)
        self.assertFalse(self.new_so.order_line.elaboration_note)
        self.new_so.order_line.elaboration_note = "custom"
        wiz = self.wizard()
        wiz_line = wiz.line_ids.filtered_domain([("product_id", "=", self.prod_2.id)])
        self.assertTrue(wiz_line)
        self.assertEqual(wiz_line.elaboration_ids, self.elab_2)
        self.assertEqual(wiz_line.elaboration_note, "custom")
