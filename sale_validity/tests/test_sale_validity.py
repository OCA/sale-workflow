# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        so_validity._onchange_date_order()

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
