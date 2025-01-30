# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import common


class TestSaleOrderRename(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.sale_order = self.env["sale.order"]
        self.sale_order_sudo = self.sale_order.sudo()
        self.base_company = self.env.ref("base.main_company")
        self.other_company = self._create_company()

    def _create_company(self):
        return self.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )

    def test_01_two_sale_order_with_same_name_in_different_companies(self):
        so_vals = {
            "name": "Test #1",
            "partner_id": self.env.ref("base.res_partner_1").id,
        }
        self.sale_order.create(
            [
                {
                    **so_vals,
                    "company_id": self.base_company.id,
                }
            ]
        )
        self.sale_order.create(
            [
                {
                    **so_vals,
                    "company_id": self.other_company.id,
                }
            ]
        )

    def test_02_raise_exception_two_sale_order_with_same_name_in_same_company(self):
        so_vals = {
            "name": "Test #1",
            "partner_id": self.env.ref("base.res_partner_1").id,
        }
        self.sale_order.create(
            [
                {
                    **so_vals,
                    "company_id": self.base_company.id,
                }
            ]
        )
        with self.assertRaises(UserError):
            self.sale_order.create(
                [
                    {
                        **so_vals,
                        "company_id": self.base_company.id,
                    }
                ]
            )

    def test_03_raise_exception_renaming_two_so_in_same_company_with_same_name(self):
        so_vals = {
            "company_id": self.base_company.id,
            "partner_id": self.env.ref("base.res_partner_1").id,
        }
        so1 = self.sale_order.create(
            [
                {
                    **so_vals,
                }
            ]
        )
        so2 = self.sale_order.create(
            [
                {
                    **so_vals,
                }
            ]
        )
        so1.write(
            {
                "name": "Test #1",
            }
        )
        with self.assertRaises(UserError):
            so2.write(
                {
                    "name": "Test #1",
                }
            )

    def test_04_allowed_renaming_two_so_in_different_company_with_same_name(self):
        so_vals = {
            "partner_id": self.env.ref("base.res_partner_1").id,
        }
        so1 = self.sale_order.create(
            [
                {
                    **so_vals,
                    "company_id": self.base_company.id,
                }
            ]
        )
        so2 = self.sale_order.create(
            [
                {
                    **so_vals,
                    "company_id": self.other_company.id,
                }
            ]
        )
        so1.write(
            {
                "name": "Test #1",
            }
        )
        so2.write(
            {
                "name": "Test #1",
            }
        )
