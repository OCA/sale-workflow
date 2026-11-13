# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleValidity(TransactionCase):
    def test_sale_validity(self):
        company = self.env.ref("base.main_company")
        company.default_sale_order_validity_days = 0
        so_no_validity = self.create_so()
        self.assertFalse(so_no_validity.validity_date)
        company.default_sale_order_validity_days = 30
        so_validity = self.create_so()
        self.assertTrue(so_validity.validity_date)
        self.assertEqual(
            so_validity.validity_date,
            fields.Date.to_date(so_validity.date_order) + relativedelta(days=30),
        )

    def test_sale_validity_recompute_on_date_order_change(self):
        company = self.env.ref("base.main_company")
        company.default_sale_order_validity_days = 30
        so = self.create_so()
        new_date_order = fields.Datetime.now() + relativedelta(days=5)
        so.date_order = new_date_order
        self.assertEqual(
            so.validity_date,
            fields.Date.to_date(new_date_order) + relativedelta(days=30),
        )

    def test_sale_validity_manual_edit_kept_without_date_order_change(self):
        company = self.env.ref("base.main_company")
        company.default_sale_order_validity_days = 30
        so = self.create_so()
        manual_date = fields.Date.to_date(so.date_order) + relativedelta(days=99)
        so.validity_date = manual_date
        so.order_line[0].product_uom_qty = 9
        self.assertEqual(so.validity_date, manual_date)

    def create_so(self):
        vals = {
            "partner_id": self.env.ref("base.res_partner_2").id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": self.env.ref("product.product_product_7").id,
                        "product_uom_qty": 8,
                    },
                )
            ],
        }
        so = self.env["sale.order"].create(vals)
        return so
