# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.sale_order_product_recommendation.tests import (
    test_recommendation_common,
)


class RecommendationCaseTests(test_recommendation_common.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier for test",
                "supplier_rank": 1,
            }
        )
        cls.supplierinfo_prod1 = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.prod_1.product_tmpl_id.id,
                "price": 150.00,
                "date_start": "2022-12-15",
                "date_end": "2022-12-15",
            }
        )
        cls.supplierinfo_prod2 = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.prod_2.product_tmpl_id.id,
                "price": 200.00,
                "date_start": "2022-12-16",
                "date_end": "2022-12-16",
            }
        )

    @freeze_time("2022-12-15")
    def test_recommendations_supplierinfo_origin_date1(self):
        wizard = self.wizard()
        wizard.origin_recommendation = "supplierinfo"
        # To avoid collision with demo data
        wizard.line_amount = 100
        wizard._generate_recommendations()
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        self.assertTrue(wiz_line_prod1)
        wiz_line_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertFalse(wiz_line_prod2)

    @freeze_time("2022-12-16")
    def test_recommendations_supplierinfo_origin_date2(self):
        wizard = self.wizard()
        wizard.origin_recommendation = "supplierinfo"
        # To avoid collision with demo data
        wizard.line_amount = 100
        wizard._generate_recommendations()
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        self.assertFalse(wiz_line_prod1)
        wiz_line_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertTrue(wiz_line_prod2)
