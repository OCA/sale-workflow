# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import new_test_user

from odoo.addons.sale.tests.common import SaleCommon


class TestProductFormTotalSold(SaleCommon):
    def test_total_sold_without_date_limit(self):
        self.sale_order.action_confirm()
        # action_confirm resets date_order to now
        self.sale_order.date_order = fields.Datetime.now() - timedelta(days=400)
        # sale.report is an SQL view
        self.env.flush_all()
        product = self.product.with_user(self.sale_manager)
        self.assertEqual(product.sales_count, 0.0)
        self.assertEqual(product.sales_total_count, 5.0)
        self.assertEqual(product.product_tmpl_id.sales_total_count, 5.0)
        for record in (product, product.product_tmpl_id):
            action = record.action_view_sales_total()
            self.assertNotIn("search_default_filter_order_date", action["context"])

    def test_total_sold_without_sales_access(self):
        self.sale_order.action_confirm()
        user = new_test_user(self.env, login="no_sales", groups="base.group_user")
        self.assertEqual(self.product.with_user(user).sales_total_count, 0.0)

    def test_total_sold_new_record(self):
        product = self.env["product.product"].new({"name": "New"})
        self.assertEqual(product.sales_total_count, 0.0)
