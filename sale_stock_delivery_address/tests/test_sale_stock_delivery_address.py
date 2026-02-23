# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestStockSourcingAddressCommon


class TestStockSourcingAddress(TestStockSourcingAddressCommon):
    def test_01_one_address_per_line(self):
        self.line_1.dest_address_id = self.address_1
        self.line_2.dest_address_id = self.address_2
        self.so.action_confirm()
        self.assertEqual(len(self.so.picking_ids), 2)
        self.assertNotEqual(
            self.so.picking_ids[0].partner_id, self.so.picking_ids[1].partner_id
        )
        move_1 = self.move_model.search([("sale_line_id", "=", self.line_1.id)])
        self.assertEqual(move_1.picking_id.partner_id, self.address_1)
        move_2 = self.move_model.search([("sale_line_id", "=", self.line_2.id)])
        self.assertEqual(move_2.picking_id.partner_id, self.address_2)

    def test_02_default_address(self):
        self.line_1.dest_address_id = self.address_1
        self.so.action_confirm()
        self.assertEqual(len(self.so.picking_ids), 2)
        move_1 = self.move_model.search([("sale_line_id", "=", self.line_1.id)])
        self.assertEqual(move_1.picking_id.partner_id, self.address_1)
        move_2 = self.move_model.search([("sale_line_id", "=", self.line_2.id)])
        # Address in header should have been used:
        self.assertEqual(move_2.picking_id.partner_id, self.partner)

    def test_03_different_stock_location(self):
        # Use a different customer location in one of the addresses:
        self.address_1.property_stock_customer = self.customer_loc_secondary
        self.line_1.dest_address_id = self.address_1
        self.line_2.dest_address_id = self.address_2
        self.so.action_confirm()
        self.assertEqual(len(self.so.picking_ids), 2)
        move_1 = self.move_model.search([("sale_line_id", "=", self.line_1.id)])
        self.assertEqual(move_1.picking_id.partner_id, self.address_1)
        self.assertEqual(move_1.location_dest_id, self.customer_loc_secondary)
        move_2 = self.move_model.search([("sale_line_id", "=", self.line_2.id)])
        self.assertEqual(move_2.picking_id.partner_id, self.address_2)
        self.assertEqual(move_2.location_dest_id, self.customer_loc_default)
