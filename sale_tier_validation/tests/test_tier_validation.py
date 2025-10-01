# Copyright 2020 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSaleTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get sale order model
        cls.so_model = cls.env.ref("sale.model_sale_order")

        # Create users
        group_ids = (
            cls.env.ref("base.group_system")
            + cls.env.ref("sales_team.group_sale_salesman_all_leads")
        ).ids
        cls.test_user_1 = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_ids)],
                "email": "test@examlple.com",
            }
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

    def test_tier_validation_model_name(self):
        self.assertIn(
            "sale.order", self.tier_def_obj._get_tier_validation_model_names()
        )

    def test_validation_sale_order(self):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
                "pricelist_id": self.customer.property_product_pricelist.id,
            }
        )
        with self.assertRaises(ValidationError):
            so.action_confirm()
        so.order_line.price_unit = 45
        so.request_validation()
        so.with_user(self.test_user_1).validate_tier()
        so.action_confirm()
        self.assertEqual(so.state, "sale")

    def test_block_print_unvalidated_sale_order(self):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
            }
        )
        so.company_id.sale_report_print_block = True
        report = self.env["report.sale.report_saleorder"]
        # Attempt to render the report before validation
        with self.assertRaises(UserError):
            report._get_report_values(docids=[so.id])
        so.request_validation()
        with self.assertRaises(UserError):
            report._get_report_values(docids=[so.id])
        so.with_user(self.test_user_1).validate_tier()
        # Attempt to render the report after validation
        report._get_report_values(docids=[so.id])
