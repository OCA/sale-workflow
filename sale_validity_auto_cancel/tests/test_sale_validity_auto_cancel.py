# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleValidityAutoCancel(TransactionCase):
    def test_sale_validity_auto_cancel(self):
        company = self.env.ref("base.main_company")
        company.sale_validity_auto_cancel_days = 10
        so = self.create_so()
        so.validity_date = fields.Date.today() - relativedelta(days=11)
        self.assertEqual(so.state, "draft")
        so.cron_sale_validity_auto_cancel()
        self.assertEqual(so.state, "cancel")

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
