# Copyright 2020 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get sale order model
        cls.so_model = cls.env.ref("sale.model_sale_order")
        # Create users
        cls.test_user_1 = new_test_user(
            cls.env,
            name="John",
            login="test1",
            groups="base.group_system, sales_team.group_sale_salesman_all_leads",
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.so_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('amount_untaxed', '>', 50.0)]",
            }
        )
        cls.customer = cls.env["res.partner"].create({"name": "Partner for test"})
        cls.product = cls.env["product.product"].create(
            {"name": "Product for test", "list_price": 120.00}
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": "Test line",
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": cls.product.list_price,
                        },
                    )
                ],
                "pricelist_id": cls.customer.property_product_pricelist.id,
            }
        )

    def test_tier_validation_model_name(self):
        self.assertIn(
            "sale.order", self.tier_def_obj._get_tier_validation_model_names()
        )

    def test_validation_sale_order(self):
        with self.assertRaises(ValidationError):
            self.sale_order.action_confirm()
        self.sale_order.order_line.price_unit = 45
        self.sale_order.request_validation()
        self.sale_order.with_user(self.test_user_1).validate_tier()
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")

    def test_block_print_unvalidated_sale_order(self):
        self.sale_order.company_id.sale_report_print_block = True
        report = self.env["report.sale.report_saleorder"]
        # Attempt to render the report before validation
        with self.assertRaises(UserError):
            report._get_report_values(docids=[self.sale_order.id])
        self.sale_order.request_validation()
        with self.assertRaises(UserError):
            report._get_report_values(docids=[self.sale_order.id])
        self.sale_order.with_user(self.test_user_1).validate_tier()
        # Attempt to render the report after validation
        report._get_report_values(docids=[self.sale_order.id])
