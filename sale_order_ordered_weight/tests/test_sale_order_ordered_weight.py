# Copyright 2021 Manuel Calero Solís (http://www.xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleOrderOrderedWeight(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("sale.product_product_4e")

        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_dozen = self.env.ref("uom.product_uom_dozen")

        self.product.weight = 5.0
        self.product.uom_id = self.uom_unit.id

        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.sale_order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                # "name": self.product_1.name,
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.uom_unit.id,
            }
        )
        self.sale_order_line_2 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                # "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.uom_dozen.id,
            }
        )

    def test_sale_order_ordered_weight(self):
        # 10 * 5 kg * 1 (Unit) + 1 * 5 kg * 12 (Dozen)
        self.assertEqual(self.sale_order.total_ordered_weight, 110.0)
