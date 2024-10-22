# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestSaleRouteAmendment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.move_obj = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "service",
            }
        )
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.loc_stock = cls.env.ref("stock.stock_location_stock")
        vals = {
            "name": "DROP SHIPPING",
            "sequence_id": cls.env.ref("stock.seq_picking_internal").id,
            "code": "outgoing",
            "warehouse_id": cls.warehouse.id,
            "sequence_code": "DROP",
            "default_location_src_id": cls.loc_supplier.id,
            "default_location_dest_id": cls.loc_customer.id,
        }
        pick_type_drop_shipping = cls.env["stock.picking.type"].create(vals)

        vals = {
            "name": "DROP SHIP",
            "sequence": 1,
            "sale_selectable": True,
            "rule_ids": [
                (
                    0,
                    0,
                    {
                        "name": "OUTPUT => Customers",
                        "action": "pull",
                        "location_src_id": cls.loc_supplier.id,
                        "location_dest_id": cls.loc_customer.id,
                        "picking_type_id": pick_type_drop_shipping.id,
                        "procure_method": "make_to_stock",
                    },
                )
            ],
        }
        cls.route_drop = cls.env["stock.route"].create(vals)
        qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product_2.id,
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
                "new_quantity": 2.0,
            }
        )
        qty_wizard.change_product_qty()
        qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "new_quantity": 1.0,
            }
        )
        qty_wizard.change_product_qty()

    def test_amend_route(self):
        """
        Create and confirm a sale order
        The created move will use the default route Stock > Customers
        Set the route drop shipping on the move.
        => A new move is created from Vendors > Customers
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0})
                ],
            }
        )
        sale_order.action_confirm()

        picking = sale_order.picking_ids.filtered(
            lambda p: p.location_id == self.loc_stock
        )
        move = picking.move_ids
        self.assertTrue(move)

        sale_order.order_line.route_id = self.route_drop
        domain = [
            ("group_id", "=", sale_order.procurement_group_id.id),
            ("location_id", "=", self.loc_supplier.id),
            ("state", "!=", "cancel"),
        ]
        move = self.move_obj.search(domain, limit=1)
        self.assertTrue(move)

    def test_amend_route_multi_product(self):
        """
        Create and confirm a sale order with 2 products.
        Then confirm one of the move and confirm the picking (a backorder
        is created for the second move).

        If you try to update the route on the processed product, a user error is
        raised.
        If you update the route on the not yet processed product, a new move is
        created.

        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0}),
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 1.0}),
                ],
            }
        )
        sale_order.action_confirm()

        picking = sale_order.picking_ids.filtered(
            lambda p: p.location_id == self.loc_stock
        )
        moves = picking.move_ids
        self.assertTrue(moves)

        # Process the move for product 2
        move_to_confirm = moves.filtered(lambda m: m.product_id == self.product_2)

        move_to_confirm.move_line_ids.qty_done = 1.0
        picking._action_done()

        self.assertEqual(
            "done",
            picking.state,
        )

        # If you try to update the route on the line related to the product 2
        # a user error is raised
        with self.assertRaisesRegex(
            UserError, "You cannot cancel"
        ), self.env.cr.savepoint():
            sale_order.order_line.filtered(
                lambda l: l.product_id == self.product_2
            ).route_id = self.route_drop

        # If you update the route on the line related to the product 1 a new
        # move is created from Vendors > Customers
        sale_order.order_line.filtered(
            lambda l: l.product_id == self.product
        ).route_id = self.route_drop
        domain = [
            ("product_id", "=", self.product.id),
            ("group_id", "=", sale_order.procurement_group_id.id),
            ("location_id", "=", self.loc_supplier.id),
            ("state", "!=", "cancel"),
        ]
        move = self.move_obj.search(domain, limit=1)
        self.assertTrue(move)

    def test_amend_route_service(self):
        """
        Create and confirm a sale order with a service product and a stockable
        product.
        Update the route on the service product.
        -> nothing should happen and the update should be ignored
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0}),
                    (
                        0,
                        0,
                        {"product_id": self.product_service.id, "product_uom_qty": 1.0},
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        picking = sale_order.picking_ids.filtered(
            lambda p: p.location_id == self.loc_stock
        )
        move = picking.move_ids
        self.assertTrue(move)
        self.assertEqual(1, len(move))
        self.assertEqual(self.product, move.product_id)
        move.picking_id.action_assign()
        self.assertEqual(
            "assigned",
            move.state,
        )
        order_line_service = sale_order.order_line.filtered(
            lambda l: l.product_id == self.product_service
        )
        self.assertTrue(order_line_service)
        self.assertFalse(order_line_service.move_ids)
        order_line_service.route_id = self.route_drop
        self.assertFalse(order_line_service.move_ids)

    def test_sale_order_line_write_same_route(self):
        """
        In this test we check that if the route on the sale order line is
        updated with the same route, nothing happens.
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0}),
                ],
            }
        )
        sale_order.action_confirm()
        move = sale_order.order_line.move_ids
        self.assertTrue(move)
        sale_order.order_line.route_id = move.route_ids
        new_move = sale_order.order_line.move_ids
        self.assertEqual(move, new_move)
