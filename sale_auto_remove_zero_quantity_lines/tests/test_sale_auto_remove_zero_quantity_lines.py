# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleAutoRemoveZeroQuantityLines(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

    def test_sale_auto_remove_zero_quantity_lines(self):
        self.env.user.company_id.sale_auto_remove_zero_quantity_lines = True
        partner = self.env.ref("base.res_partner_1")
        p = self.env.ref("product.product_product_6")
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 0,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Note test",
                            "display_type": "line_note",
                        },
                    ),
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )
        so.action_confirm()
        self.assertEqual(len(so.order_line), 2)
