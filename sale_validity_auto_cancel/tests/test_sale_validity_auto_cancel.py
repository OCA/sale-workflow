# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
# Copyright 2026 ACSONE SA/NV (<https://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta

from odoo import Command, fields

from odoo.addons.base.tests.common import BaseCommon


class TestSaleValidityAutoCancel(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.company = cls.env.ref("base.main_company")
        cls.company.sale_validity_auto_cancel_days = 10
        cls.other_company = cls.env["res.company"].create({"name": "Other Company"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

    def create_so(self, company=None):
        if company is None:
            company = self.company
        vals = {
            "company_id": company.id,
            "partner_id": self.partner.id,
            "validity_date": fields.Date.today() - relativedelta(days=11),
            "order_line": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 8,
                    },
                )
            ],
        }
        so = self.SaleOrder.create(vals)
        return so

    def test__prepare_auto_cancel_expired_domain(self):
        """Test the domain returned by _prepare_auto_cancel_expired_domain"""
        domain = self.SaleOrder._prepare_auto_cancel_expired_domain(self.company)
        expected_threshold = fields.Date.today() - relativedelta(
            days=self.company.sale_validity_auto_cancel_days
        )
        states = self.SaleOrder._get_auto_cancel_expired_states()
        expected_domain = [
            ("company_id", "=", self.company.id),
            ("state", "in", states),
            ("validity_date", "<", expected_threshold),
            ("auto_cancel_expired_so", "=", True),
        ]
        self.assertEqual(domain, expected_domain)

    def test_sale_validity_auto_cancel_keep_so(self):
        self.partner.write({"auto_cancel_expired_so": False})
        so = self.create_so()
        self.assertEqual(so.state, "draft")
        so.cron_sale_validity_auto_cancel()
        self.assertEqual(so.state, "draft")

    def test_sale_validity_auto_cancel_specific_company(self):
        """Test that only SOs from the specified company_ids are canceled."""
        so = self.create_so()
        so_other_company = self.create_so(company=self.other_company)
        self.assertEqual(so.state, "draft")
        self.assertEqual(so_other_company.state, "draft")
        so.cron_sale_validity_auto_cancel(company_ids=[self.company.id])
        self.assertEqual(so.state, "cancel")
        self.assertEqual(so_other_company.state, "draft")

    def test_sale_validity_auto_cancel_no_companies(self):
        """Test that all companies are considered when company_ids is None."""
        so = self.create_so()
        so_other_company = self.create_so(company=self.other_company)
        self.assertEqual(so.state, "draft")
        self.assertEqual(so_other_company.state, "draft")
        so.cron_sale_validity_auto_cancel()
        self.assertEqual(so.state, "cancel")
        self.assertEqual(so_other_company.state, "cancel")
