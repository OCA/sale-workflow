# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestSaleStockOwnerRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.owner = cls.env["res.partner"].create({"name": "Owner"})
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.warehouse.delivery_steps = "pick_ship"

    def test_sale_stock_owner_restriction(self):
        warehouse = self.warehouse
        self.env["stock.quant"]._update_available_quantity(
            self.product, warehouse.lot_stock_id, 10.0, owner_id=self.owner
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "restrict_partner_id": self.owner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        # The procurement only creates the pick, the ship is pushed on validation
        pick = sale_order.picking_ids
        self.assertEqual(pick.picking_type_id, warehouse.pick_type_id)
        pick.action_assign()
        self.assertEqual(pick.owner_id, self.owner)
        self.assertEqual(pick.move_ids.restrict_partner_id, self.owner)
        self.assertEqual(pick.move_line_ids.owner_id, self.owner)
        pick.move_ids.picked = True
        pick.button_validate()
        ship = pick.move_ids.move_dest_ids.picking_id
        self.assertEqual(ship.picking_type_id, warehouse.out_type_id)
        self.assertEqual(ship.owner_id, self.owner)
        self.assertEqual(ship.move_ids.restrict_partner_id, self.owner)
        self.assertEqual(ship.move_line_ids.owner_id, self.owner)
