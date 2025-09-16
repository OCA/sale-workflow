# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form

from .sale_product_identification_common import TestSaleOrderIdentificationCommon


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
