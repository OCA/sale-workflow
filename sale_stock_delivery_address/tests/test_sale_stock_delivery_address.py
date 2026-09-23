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

    def test_procurement_group_key_no_override(self):
        """Test that the procurement group key is not overridden if no
        destination address is set on the line.
        """
        # pylint: disable=missing-return
        # Ensure dest_address_id is not set
        self.line_1.dest_address_id = False
        key = self.line_1._get_procurement_group_key()
        # The key should be exactly what the parent returns,
        # without being modified/wrapped by this module.
        parent_key = super(type(self.line_1), self.line_1)._get_procurement_group_key()
        self.assertEqual(key, parent_key)

    def test_procurement_group_key_override(self):
        """Test that the procurement group key is overridden if a
        destination address is set on the line.
        """
        # Ensure dest_address_id is set
        self.line_1.dest_address_id = self.address_1
        key = self.line_1._get_procurement_group_key()
        # The key should be (15, address_id)
        expected_key = (15, self.address_1)
        self.assertEqual(key, expected_key)
