# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
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
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_7")

    def create_so(self):
        vals = {
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

    def test_sale_validity_auto_cancel(self):
        so = self.create_so()
        self.assertEqual(so.state, "draft")
        so.cron_sale_validity_auto_cancel()
        self.assertEqual(so.state, "cancel")

    def test_sale_validity_auto_cancel_keep_so(self):
        self.partner.write({"auto_cancel_expired_so": False})
        so = self.create_so()
        self.assertEqual(so.state, "draft")
        so.cron_sale_validity_auto_cancel()
        self.assertEqual(so.state, "draft")
