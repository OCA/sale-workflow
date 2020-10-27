# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleStock(TransactionCase):
    def setUp(self):
        super(TestSaleStock, self).setUp()
        partner = self.env.ref("base.res_partner_1")
        product = self.env.ref("product.product_delivery_01")
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": product.uom_id.id,
                        },
                    )
                ],
            }
        )

    def test_sale_stock_picking_validation_blocked(self):
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.move_lines.write({"quantity_done": 1})
        self.sale_order.action_block_picking_validation()
        self.assertFalse(picking.show_validate)
        with self.assertRaises(ValidationError):
            picking.button_validate()
        self.sale_order.action_unblock_picking_validation()
        self.assertTrue(picking.show_validate)
        picking.button_validate()
