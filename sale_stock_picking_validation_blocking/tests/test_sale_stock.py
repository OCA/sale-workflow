# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env.ref("base.res_partner_1")
        product = cls.env.ref("product.product_delivery_01")
        cls.sale_order = cls.env["sale.order"].create(
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
        self.assertTrue(self.sale_order.hide_button_picking_validation_blocked)
        self.sale_order.action_confirm()
        self.assertFalse(self.sale_order.hide_button_picking_validation_blocked)
        picking = self.sale_order.picking_ids
        picking.move_ids.write({"quantity": 1})
        self.assertFalse(self.sale_order.picking_validation_blocked)
        self.sale_order.action_block_picking_validation()
        self.assertTrue(self.sale_order.picking_validation_blocked)
        with self.assertRaises(ValidationError):
            picking.button_validate()
        self.sale_order.action_unblock_picking_validation()
        picking.button_validate()
