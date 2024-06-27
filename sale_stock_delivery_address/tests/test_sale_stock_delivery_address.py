# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockSourcingAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]
        cls.warehouse_model = cls.env["stock.warehouse"]
        cls.move_model = cls.env["stock.move"]
        cls.location_model = cls.env["stock.location"]

        # Check for existence of models before use
        cls.route_model = cls.env.get("stock.location.route")
        cls.rule_model = cls.env.get("stock.rule")

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer_loc_default = cls.env.ref("stock.stock_location_customers")
        cls.customer_loc_secondary = cls.location_model.create(
            {"name": "Test customer location", "usage": "customer"}
        )
        cls.partner = cls.partner_model.create({"name": "Test partner"})
        cls.address_1 = cls.partner_model.create(
            {"name": "Address 1", "parent_id": cls.partner.id, "type": "delivery"}
        )
        cls.address_2 = cls.partner_model.create(
            {"name": "Address 2", "parent_id": cls.partner.id, "type": "delivery"}
        )
        cls.product = cls.product_model.create(
            {"name": "Test product", "type": "product"}
        )

        if cls.route_model:
            # Create route for secondary customer location:
            cls.secondary_route = cls.route_model.create(
                {
                    "warehouse_selectable": True,
                    "name": "Ship to customer sec location",
                    "warehouse_ids": [(6, 0, cls.warehouse.ids)],
                }
            )
            if cls.rule_model:
                cls.wh2_rule = cls.rule_model.create(
                    {
                        "location_id": cls.customer_loc_secondary.id,
                        "location_src_id": cls.warehouse.lot_stock_id.id,
                        "action": "pull_push",
                        "warehouse_id": cls.warehouse.id,
                        "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                        "name": "Stock -> Customers 2",
                        "route_id": cls.secondary_route.id,
                    }
                )

        # Create a SO with a couple of lines:
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": cls.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": cls.product.list_price,
                        },
                    ),
                ],
            }
        )
        cls.line_1 = cls.so.order_line[0]
        cls.line_2 = cls.so.order_line[1]

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
