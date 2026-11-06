# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from unittest.mock import patch

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.tests import Form

from .sale_product_identification_common import TestSaleOrderIdentificationCommon

PATH_MODELS = "odoo.addons.sale_product_identification.models."
PATH_NORMALIZE_VALUE = PATH_MODELS + (
    "product_template_id_category.ProductTemplateIdcategory._normalize_value"
)
PATH_TEST_EXPRESSION = PATH_MODELS + (
    "product_template_id_category.ProductTemplateIdcategory._test_python_expr"
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
        today = fields.Date.context_today(self.env.user)
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

    def test_eval_value_without_expression(self):
        product_tmpl, _ = self.valid_extra_identification(False)

        prod_category = product_tmpl.product_tmpl_category_ids
        self.assertFalse(prod_category.value)
        self.assertTrue(prod_category._test_python_expr())
        self.assertTrue(prod_category._eval_value(self.order))

    def test_identification_domain_without_partner(self):
        ResPartnerIdNumber = self.env["res.partner.id_number"]

        self.assertEqual(ResPartnerIdNumber._identification_domain(), Domain.TRUE)
        self.assertEqual(
            ResPartnerIdNumber._identification_domain(partner_id=False), Domain.TRUE
        )

    def test_identification_domain_with_partner(self):
        other_partner = self.env["res.partner"].create(
            {
                "name": "Other Partner",
                "id_numbers": [
                    Command.create(
                        {
                            "name": "Other ID",
                            "category_id": self.category_corrosive.id,
                        }
                    )
                ],
            }
        )
        ResPartnerIdNumber = self.env["res.partner.id_number"]

        id_numbers = ResPartnerIdNumber.search(
            ResPartnerIdNumber._identification_domain(partner_id=self.partner_id.id)
        )

        self.assertEqual(id_numbers, self.partner_id.id_numbers)
        self.assertNotIn(other_partner.id_numbers, id_numbers)

    def test_message_error_identifications_without_matching_category(self):
        message = self.env["res.partner.id_number"].message_error_identifications(
            self.product_tmpl_with_iden, [self.category_explosive.id], True
        )

        self.assertEqual(message, "")

    def test_message_error_identifications_required(self):
        self.product_tmpl_with_iden.product_tmpl_category_ids.filtered(
            lambda x: x.category_id == self.category_corrosive
        ).message = "Handle with care"

        message = self.env["res.partner.id_number"].message_error_identifications(
            self.product_tmpl_with_iden
            + self.product_tmpl_with_iden_opt
            + self.product_tmpl_without_iden,
            [self.category_corrosive.id, self.category_bilogical.id],
            required=True,
        )

        self.assertEqual(
            message,
            "\nProduct Test Iden"
            "\n • Corrosive (Handle with care)"
            "\n • Bilogical "
            "\nProduct Test optional"
            "\n • Bilogical ",
        )

    def test_message_error_identifications_optional(self):
        message = self.env["res.partner.id_number"].message_error_identifications(
            self.product_tmpl_with_iden + self.product_tmpl_with_iden_opt,
            [self.category_corrosive.id, self.category_explosive.id],
        )

        self.assertEqual(
            message,
            "\nProduct Test optional\n • Corrosive \n • Explosive ",
        )

    def test_validate_identification_partner_without_id_numbers(self):
        partner = self.env["res.partner"].create({"name": "Partner Without IDs"})
        ResPartnerIdNumber = self.env["res.partner.id_number"]

        self.assertFalse(
            ResPartnerIdNumber.validate_identification(partner_id=partner.id)
        )
        requested_categories = self.category_corrosive + self.category_explosive
        self.assertEqual(
            ResPartnerIdNumber.validate_identification(
                partner_id=partner.id,
                compare_identification_ids=requested_categories,
            ),
            requested_categories,
        )

    def test_validate_identification_validity_boundaries(self):
        today = fields.Date.context_today(self.env.user)
        IdCategory = self.env["res.partner.id_category"]
        started_category = IdCategory.create({"code": "id_started", "name": "Started"})
        not_expired_category = IdCategory.create(
            {"code": "id_not_expired", "name": "Not expired"}
        )
        expired_range_category = IdCategory.create(
            {"code": "id_expired_range", "name": "Expired range"}
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Partner Validity Boundaries",
                "id_numbers": [
                    Command.create(
                        {
                            "name": "Started ID",
                            "category_id": started_category.id,
                            "valid_from": today - timedelta(days=1),
                        }
                    ),
                    Command.create(
                        {
                            "name": "Not Expired ID",
                            "category_id": not_expired_category.id,
                            "valid_until": today + timedelta(days=1),
                        }
                    ),
                    Command.create(
                        {
                            "name": "Expired Range ID",
                            "category_id": expired_range_category.id,
                            "valid_from": today - timedelta(days=10),
                            "valid_until": today - timedelta(days=1),
                        }
                    ),
                ],
            }
        )

        valid_categories = self.env["res.partner.id_number"].validate_identification(
            partner_id=partner.id
        )

        self.assertEqual(valid_categories, started_category + not_expired_category)

    def test_validate_identification_invalid_id_number(self):
        self.category_corrosive.validation_code = "failed = True"

        with self.assertRaises(ValidationError):
            self.env["res.partner.id_number"].validate_identification(
                partner_id=self.partner_id.id
            )

    def test_action_confirm_without_identifications(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product_tmpl_without_iden.name,
                            "product_id": self.product_without_iden.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

        order.action_confirm()

        self.assertEqual(order.state, "sale")
