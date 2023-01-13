# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form, TransactionCase


class TestSaleMissingTracking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "sale_missing_tracking": True}
        )
        cls.regular_product = cls.env["product.product"].create(
            {
                "name": "Test regular product",
                "type": "consu",
                "lst_price": 700.00,
                "sale_missing_tracking": True,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "lst_price": 800.00,
            }
        )
        cls.old_sale_order = cls._create_sale_order(cls.regular_product)
        cls.old_sale_order.action_confirm()
        cls.old_sale_order.date_order = (fields.Date.today()) - relativedelta(months=1)
        # Reset the company's default configuration options
        cls.old_sale_order.company_id.sale_missing_max_delay_times = 1
        cls.old_sale_order.company_id.sale_missing_days_from = 45
        cls.old_sale_order.company_id.sale_missing_days_to = 15
        cls.old_sale_order.company_id.sale_missing_days_notification = 30
        cls.old_sale_order.company_id.sale_missing_months_consumption = 12
        cls.old_sale_order.company_id.sale_missing_minimal_consumption = 1000.0
        cls.new_sale_order = cls._create_sale_order(cls.product)

    @classmethod
    def _create_sale_order(cls, product):
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = 2.0
        return order_form.save()

    def test_missing_tracking_count(self):
        trackings = self.new_sale_order.missing_tracking_count
        self.assertTrue(trackings == 0)
        action = self.new_sale_order.action_confirm()
        wiz = self.env["sale.missing.tracking.wiz"].browse(action["res_id"])
        self.assertEqual(
            wiz.missing_tracking_ids.product_id.name, "Test regular product"
        )
