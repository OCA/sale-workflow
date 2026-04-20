# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from unittest.mock import patch

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

from .sale_product_identification_common import TestSaleOrderIdentificationCommon

PATH_MODELS = "odoo.addons.sale_product_identification.models."
PATH_NORMALIZE_VALUE = PATH_MODELS + (
    "product_template_id_category." "ProductTemplateIdcategory._normalize_value"
)
PATH_TEST_EXPRESSION = PATH_MODELS + (
    "product_template_id_category." "ProductTemplateIdcategory._test_python_expr"
)


class TestSaleOrderIdentification(TestSaleOrderIdentificationCommon):
    def test_action_confirm(self):
        with self.assertRaises(ValidationError):
            self.order.action_confirm()
        self.assertEqual(self.order.state, "draft")

        self.partner_id.id_numbers = [
            Command.create(
                {
                    "name": "Bad X ID",
                    "category_id": self.category_bilogical.id,
                }
            )
        ]
        self.order.action_confirm()
        self.assertEqual(self.order.state, "sale")

        self.order_opt.action_confirm()
        self.assertEqual(self.order_opt.state, "draft")
        message = self.order_opt._message_error_identifications(
            [self.category_bilogical.id], True
        )
        self.assertIn(self.product_tmpl_with_iden_opt.name, message)
        self.assertIn(self.category_bilogical.name, message)
        ConfirmIdentification = self.env["confirm.identification"].with_context(
            **{
                "default_order_ids": [Command.set(self.order_opt.ids)],
                "default_message": message,
            }
        )
        wizard_confirm_identification_form = Form(ConfirmIdentification)
        wizard_confirm_identification = wizard_confirm_identification_form.save()
        wizard_confirm_identification.confirm_identification()
        self.assertEqual(self.order_opt.state, "sale")

    def test_action_confirm_skips_optional_identification_with_context(self):
        self.partner_id.id_numbers = [
            Command.create(
                {
                    "name": "Required ID",
                    "category_id": self.category_bilogical.id,
                }
            )
        ]

        self.order_opt.with_context(
            not_verify_optional_identification=True
        ).action_confirm()

        self.assertEqual(self.order_opt.state, "sale")

    def test_validate_identification_id_number(self):
        ResPartnerIdNumber = self.env["res.partner.id_number"]
        with self.assertRaises(ValidationError):
            ResPartnerIdNumber.validate_identification(
                **{
                    "partner_id": False,
                }
            )
        category_ids = ResPartnerIdNumber.validate_identification(
            **{
                "partner_id": self.partner_id.id,
            }
        )
        self.assertEqual(len(category_ids), 1)
        self.assertEqual(category_ids[:1], self.category_corrosive)

        self.partner_id.id_numbers = [
            Command.create(
                {
                    "name": "Test category",
                    "category_id": self.category_bilogical.id,
                }
            )
        ]

        category_ids = ResPartnerIdNumber.validate_identification(
            **{
                "partner_id": self.partner_id.id,
                "compare_identification_ids": self.category_corrosive
                + self.category_bilogical,
            }
        )
        self.assertEqual(len(category_ids), 0)

    def test_validate_identification_uses_validity_dates(self):
        today = fields.Date.today()
        expired_category = self.env["res.partner.id_category"].create(
            {"code": "id_expired", "name": "Expired"}
        )
        future_category = self.env["res.partner.id_category"].create(
            {"code": "id_future", "name": "Future"}
        )
        valid_category = self.env["res.partner.id_category"].create(
            {"code": "id_valid", "name": "Valid"}
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Partner Validity Test",
                "id_numbers": [
                    Command.create(
                        {
                            "name": "Expired ID",
                            "category_id": expired_category.id,
                            "valid_until": today - timedelta(days=1),
                        }
                    ),
                    Command.create(
                        {
                            "name": "Future ID",
                            "category_id": future_category.id,
                            "valid_from": today + timedelta(days=1),
                        }
                    ),
                    Command.create(
                        {
                            "name": "Valid ID",
                            "category_id": valid_category.id,
                            "valid_from": today,
                            "valid_until": today,
                        }
                    ),
                ],
            }
        )

        expected_missing_categories = expired_category + future_category
        requested_categories = expected_missing_categories + valid_category

        missing_categories = self.env["res.partner.id_number"].validate_identification(
            partner_id=partner.id,
            compare_identification_ids=requested_categories,
        )

        self.assertEqual(missing_categories, expected_missing_categories)

    def valid_extra_identification(self, expression="1 == 10"):
        product_tmpl_category = self.env["product.template.id_category"].create(
            {
                "category_id": self.category_corrosive.id,
                "is_mandatory": True,
                "value": expression,
            }
        )
        self.partner_id.id_numbers = [
            Command.create(
                {
                    "name": "Test category",
                    "category_id": self.category_bilogical.id,
                }
            )
        ]
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Product Test Extra Iden",
                "required_identification": True,
                "product_tmpl_category_ids": [Command.set([product_tmpl_category.id])],
            }
        )
        product = product_tmpl.product_variant_ids[:1]
        return product_tmpl, product

    def test_extra_identification_failed(self):
        product_tmpl, product = self.valid_extra_identification()
        self.order.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": product_tmpl.name,
                            "product_id": product.id,
                            "product_uom_qty": 5,
                        }
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            self.order.action_confirm()
        self.assertEqual(self.order.state, "draft")

    def test_extra_identification(self):
        product_tmpl, product = self.valid_extra_identification("result = 1 == 1")
        self.order.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": product_tmpl.name,
                            "product_id": product.id,
                            "product_uom_qty": 10,
                        }
                    )
                ],
            }
        )
        self.order.action_confirm()
        self.assertEqual(self.order.state, "sale")

    def test_duplicate_identification_categories_are_rejected(self):
        with self.assertRaises(ValidationError) as error:
            self.env["product.template"].create(
                {
                    "name": "Product Test Duplicate Iden",
                    "required_identification": True,
                    "product_tmpl_category_ids": [
                        Command.create(
                            {
                                "category_id": self.category_corrosive.id,
                                "is_mandatory": True,
                            }
                        ),
                        Command.create(
                            {
                                "category_id": self.category_corrosive.id,
                                "is_mandatory": False,
                            }
                        ),
                    ],
                }
            )

        self.assertIn(self.category_corrosive.name, str(error.exception))

    def test_expression_python_failed(self):
        product_tmpl, product = self.valid_extra_identification()
        with patch(PATH_NORMALIZE_VALUE) as normalize_value:
            product_tmpl_form = Form(product_tmpl)
            with product_tmpl_form.product_tmpl_category_ids.edit(
                0
            ) as product_tmpl_category_form:
                product_tmpl_category_form.value = "result ="
            normalize_value.assert_called_once()
            with self.assertRaises(ValidationError):
                product_tmpl_form.save()

    def test_expression_python_success(self):
        product_tmpl, product = self.valid_extra_identification()
        with (
            patch(PATH_NORMALIZE_VALUE) as normalize_value,
            patch(PATH_TEST_EXPRESSION) as test_expression,
        ):
            product_tmpl_form = Form(product_tmpl)
            with product_tmpl_form.product_tmpl_category_ids.edit(
                0
            ) as product_tmpl_category_form:
                product_tmpl_category_form.value = "result = 1 == 1"
                product_tmpl_category_form.save()
            product_tmpl_form.save()
            normalize_value.assert_called_once()
            test_expression.assert_called_once()

        with (
            patch(PATH_NORMALIZE_VALUE) as normalize_value,
            patch(PATH_TEST_EXPRESSION) as test_expression,
        ):
            product_tmpl_form = Form(product_tmpl)
            with product_tmpl_form.product_tmpl_category_ids.edit(
                0
            ) as product_tmpl_category_form:
                product_tmpl_category_form.value = "# Test True"
            product_tmpl_form.save()
            normalize_value.assert_called_once()
            test_expression.assert_called_once()

    def test_normalize_value(self):
        product_tmpl, _ = self.valid_extra_identification()

        value = product_tmpl.product_tmpl_category_ids._normalize_value(
            "\tresult = 1 == 1    \r\n"
        )

        self.assertEqual(value, "result = 1 == 1")

    def test_eval_value(self):
        product_tmpl, _ = self.valid_extra_identification("result = [1] + 1")
        with self.assertRaises(ValidationError):
            product_tmpl.product_tmpl_category_ids._eval_value(None)

    def test_eval_value_ignores_comment_only_expression(self):
        product_tmpl, _ = self.valid_extra_identification("# result = False")

        self.assertTrue(product_tmpl.product_tmpl_category_ids._eval_value(self.order))
