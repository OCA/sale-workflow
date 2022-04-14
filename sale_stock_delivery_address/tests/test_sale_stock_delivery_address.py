# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestStockSourcingAddress(TransactionCase):
    def setUp(self):
        super(TestStockSourcingAddress, self).setUp()
        self.partner_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        self.warehouse_model = self.env["stock.warehouse"]
        self.move_model = self.env["stock.move"]
        self.location_model = self.env["stock.location"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.customer_loc_default = self.env.ref("stock.stock_location_customers")
        self.customer_loc_secondary = self.location_model.create(
            {"name": "Test customer location", "usage": "customer"}
        )
        self.partner = self.partner_model.create({"name": "Test partner"})
        self.address_1 = self.partner_model.create(
            {"name": "Address 1", "parent_id": self.partner.id, "type": "delivery"}
        )
        self.address_2 = self.partner_model.create(
            {"name": "Address 2", "parent_id": self.partner.id, "type": "delivery"}
        )
        self.product = self.product_model.create(
            {"name": "Test product", "type": "product"}
        )

        # Create route for secondary customer location:
        self.secondary_route = self.env["stock.location.route"].create(
            {
                "warehouse_selectable": True,
                "name": "Ship to customer sec location",
                "warehouse_ids": [(6, 0, self.warehouse.ids)],
            }
        )
        self.wh2_rule = self.env["stock.rule"].create(
            {
                "location_id": self.customer_loc_secondary.id,
                "location_src_id": self.warehouse.lot_stock_id.id,
                "action": "pull_push",
                "warehouse_id": self.warehouse.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "name": "Stock -> Customers 2",
                "route_id": self.secondary_route.id,
            }
        )

        # Create a SO with a couple of lines:
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
            }
        )
        self.line_1 = self.so.order_line[0]
        self.line_2 = self.so.order_line[1]

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
