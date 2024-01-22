# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.addons.sale_order_product_recommendation.tests.test_recommendation_common import (
    RecommendationCase,
)


class TestSale(RecommendationCase):
    @freeze_time("2021-10-02 15:30:00")
    def test_sale_product_recomendation_multi_add(self):
        """Test that the recommended products are added to the order"""
        self.enable_force_zero_units_included()
        so = self.env["sale.order"].create({"partner_id": self.partner.id})
        so.sale_order_recommendation_quick_add_action()
        self.assertEqual(len(so.order_line), 3)
