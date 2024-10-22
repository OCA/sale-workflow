# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Date

from .common import SaleCountryRestrictionCommon


class TestSaleRestriction(SaleCountryRestrictionCommon):
    def test_sale_restriction(self):
        with patch.object(fields.Date, "today") as today:
            today.return_value = Date.to_date("2018-03-20")
            so = self._create_so(partner=self.partner, product=self.product_2)
            with self.assertRaises(ValidationError):
                so.action_confirm()

    def test_sale_restriction_inverse(self):
        self.env.company.country_restriction_strategy = "restrict"
        with patch.object(fields.Date, "today") as today:
            today.return_value = Date.to_date("2018-03-20")
            so = self._create_so(partner=self.partner, product=self.product_2)
            so.action_confirm()

    def test_sale_restriction_no_match(self):
        # Add a restriction that does not match shipping id
        self.partner.country_restriction_id = self.restriction_1
        with patch.object(fields.Date, "today") as today:
            today.return_value = Date.to_date("2018-03-20")
            so = self._create_so(partner=self.partner, product=self.product_2)
            so.action_confirm()

    def test_sale_restriction_partner(self):
        self.partner.country_restriction_id = False
        self.line_obj.create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product_2.id,
            }
        )
        self.sale_order = self._create_so(
            partner=self.partner, product=self.product_2, partner_shipping=self.partner
        )
        with self.assertRaises(ValidationError):
            self.sale_order.action_confirm()

        self.partner.country_restriction_id = self.restriction_1
        self.sale_order.action_confirm()
        self.assertEqual(
            "sale",
            self.sale_order.state,
        )

    def test_partner(self):
        self.partner.country_id = False
        vals = {
            "partner_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
        }

        self.sale_order = self.env["sale.order"].new(vals)
        res = self.sale_order._onchange_partners_check_country()
        self.assertIn("warning", res)

        self.partner.country_id = self.kp
        res = self.sale_order._onchange_partners_check_country()
        self.assertNotIn("warning", res)

        self.partner.country_restriction_id = False
        res = self.sale_order._onchange_partners_check_restriction()
        self.assertIn("warning", res)
