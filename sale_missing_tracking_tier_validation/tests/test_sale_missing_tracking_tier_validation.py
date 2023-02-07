# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, new_test_user, users


class TestSaleMissingTrackingTierValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create user
        cls.user = new_test_user(
            cls.env,
            login="user",
            groups="base.group_system, sales_team.group_sale_salesman_all_leads",
        )
        cls.admin = cls.env.ref("base.user_admin")
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
        # Create an old sale order
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
        # Create a new sale order
        cls.new_sale_order = cls._create_sale_order(cls.product)
        # Create tier definitions:
        cls.tier_definition = cls._create_tier_definition(cls)

    @classmethod
    def _create_sale_order(cls, product):
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        order_form.user_id = cls.user
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = 3.0
        return order_form.save()

    def _create_tier_definition(self):
        te_model = self.env.ref(
            "sale_missing_tracking.model_sale_missing_tracking_exception"
        )
        definition = self.env["tier.definition"].create(
            {
                "model_id": te_model.id,
                "review_type": "individual",
                "reviewer_id": self.admin.id,
                "definition_domain": "[['consumption', '>', 2000]]",
            }
        )
        return definition

    def test_tier_validation_model_name(self):
        self.assertIn(
            "sale.missing.tracking.exception",
            self.env["tier.definition"]._get_tier_validation_model_names(),
        )

    @users("user")
    def test_validation_missing_tracking_exception(self):
        action = self.new_sale_order.action_confirm()
        wiz = self.env["sale.missing.tracking.wiz"].browse(action["res_id"])
        exception = wiz.missing_tracking_ids.action_create_exception()
        with self.assertRaises(ValidationError):
            exception.action_approve()
        self.assertEqual(exception.state, "request")
        exception.with_user(self.admin).validate_tier()
        exception.action_approve()
        self.assertEqual(exception.state, "approved")
