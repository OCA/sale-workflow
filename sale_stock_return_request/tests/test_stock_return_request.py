# Copyright 2019 Tecnativa - David Vidal
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.stock_return_request.tests.test_stock_return_request_common import (
    StockReturnRequestCase,
)


class SaleReturnRequestCase(StockReturnRequestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_customer_2 = cls.env["res.partner"].create(
            {
                "name": "Mr. Sale",
                "property_stock_supplier": cls.supplier_loc.id,
                "property_stock_customer": cls.customer_loc.id,
            }
        )
        cls.partner_customer_3 = cls.env["res.partner"].create(
            {
                "name": "Mr. Sale 3",
                "property_stock_supplier": cls.supplier_loc.id,
                "property_stock_customer": cls.customer_loc.id,
            }
        )
        cls.wh1.delivery_route_id.rule_ids.location_dest_id = cls.customer_loc.id
        # Force location_dest_id to be taken from the route
        # instead of the picking type's location_dest_id
        cls.wh1.delivery_route_id.rule_ids.location_dest_from_rule = True
        cls.so_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_customer_2.id,
                "warehouse_id": cls.wh1.id,
                "picking_policy": "direct",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.prod_3.id,
                            "name": cls.prod_3.name,
                            "product_uom_qty": 14.0,
                            "price_unit": 10.0,
                            "product_uom": cls.prod_3.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.so_2 = cls.so_1.copy()
        cls.sale_orders = cls.so_1 | cls.so_2
        # Confirm all the sale orders
        for order in cls.sale_orders:
            order.action_confirm()
        # Deliver products. For each picking:
        # 10 units of TSTPROD3LOT0001 -> -20 units of 70 already existing
        # 4 units of TSTPROD3LOT0002 -> -8 units of 0 already existing
        for picking in cls.sale_orders.mapped("picking_ids"):
            picking.move_line_ids.unlink()
            move = picking.move_ids
            vals = {
                "move_id": move.id,
                "picking_id": picking.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_uom_id": move.product_uom.id,
                "product_id": move.product_id.id,
                "lot_id": cls.prod_3_lot1.id,
                "quantity": 10.0,
            }
            cls.env["stock.move.line"].create(vals)
            vals["lot_id"] = cls.prod_3_lot2.id
            vals["quantity"] = 4
            cls.env["stock.move.line"].create(vals)
            picking.button_validate()

    def test_01_return_sale_stock_from_customer(self):
        """Return stock from customer and the corresponding
        sales will be ready for refund"""
        self.return_request_customer.write(
            {
                "partner_id": self.partner_customer_2.id,
                "to_refund": True,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot1.id,
                            "quantity": 12.0,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot2.id,
                            "quantity": 4.0,
                        },
                    ),
                ],
            }
        )
        self.return_request_customer.action_confirm()
        sale_orders = self.return_request_customer.sale_order_ids
        pickings = self.return_request_customer.returned_picking_ids
        moves = self.return_request_customer.returned_picking_ids.mapped("move_ids")
        # For lot TSTPROD3LOT0001 we'll be returning:
        # ==> 10 units from SO01
        # ==> 2 units from SO02
        # For lot TSTPROD3LOT0002 we'll be returning:
        # ==> 4 units from SO01
        self.assertEqual(len(sale_orders), 2)
        self.assertEqual(len(pickings), 2)
        # Two moves with two move lines each
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(sum(moves.mapped("product_uom_qty")), 16.0)
        # Process the return to validate all the pickings
        self.return_request_customer.action_validate()
        self.assertTrue(
            all([True if x == "done" else False for x in pickings.mapped("state")])
        )
        # For lot TSTPROD3LOT0001 we had 50 units
        prod_3_qty_lot_1 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id, lot_id=self.prod_3_lot1.id
        ).qty_available
        # For lot TSTPROD3LOT0002 we had -8 units
        prod_3_qty_lot_2 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id, lot_id=self.prod_3_lot2.id
        ).qty_available
        self.assertAlmostEqual(prod_3_qty_lot_1, 62.0)
        self.assertAlmostEqual(prod_3_qty_lot_2, -4.0)
        # There were 28 units in the sale orders.
        self.assertAlmostEqual(
            sum(sale_orders.mapped("order_line.qty_delivered")), 12.0
        )
        # Test the view action
        res = self.return_request_customer.action_view_sales()
        expected_res = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "domain": f"[('id', 'in', {sorted(sale_orders.ids)})]",
        }
        # The intention is to check if a dictionary is a subset of other.
        # As assertDictContainsSubset() is no longer supported,
        # this is an alternative way of checking.
        self.assertEqual(res, {**res, **expected_res})

    def test_02_return_sale_stock_from_customer_single_sale(self):
        """Return stock from customer with a single result"""
        self.return_request_customer.write(
            {
                "partner_id": self.partner_customer_2.id,
                "to_refund": True,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot1.id,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        self.return_request_customer.action_confirm()
        sale_order = self.return_request_customer.sale_order_ids
        self.assertEqual(len(sale_order), 1)
        # Test the view action
        res = self.return_request_customer.action_view_sales()
        expedcted_res = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [(self.env.ref("sale.view_order_form").id, "form")],
            "res_id": sale_order.id,
        }
        self.assertEqual(res, {**res, **expedcted_res})

    def test_03_return_sale_stock_from_customer_sale_filtered(self):
        """Check return stock from customer filtered by sales order"""
        self.return_request_customer.write(
            {
                "partner_id": self.partner_customer_2.id,
                "to_refund": True,
                "filter_sale_order_ids": [(4, self.so_1.id)],
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot1.id,
                            "quantity": 3.0,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot2.id,
                            "quantity": 4.0,
                        },
                    ),
                ],
            }
        )
        self.assertTrue(self.return_request_customer.filter_sale_order_ids)
        self.return_request_customer.partner_id = self.partner_customer_3
        self.return_request_customer._onchange_partner_id_sale_stock_return_request()
        self.assertFalse(self.return_request_customer.filter_sale_order_ids)
        self.return_request_customer.partner_id = self.partner_customer_2
        self.return_request_customer.filter_sale_order_ids = [(4, self.so_1.id)]
        move_domain = self.return_request_customer.line_ids[0]._get_moves_domain()
        self.assertEqual(move_domain[-1][2], self.so_1.ids)
        self.return_request_customer.action_confirm()
        sale_orders = self.return_request_customer.sale_order_ids
        self.assertEqual(len(sale_orders), 1)

    def test_04_return_sale_stock_sale_order(self):
        returnable_lines = self.so_1._get_returnable_lines()
        self.assertEqual(len(returnable_lines), 1)
        self.assertTrue(self.so_1.show_create_return_request)
        action = self.so_1.action_create_return_request()
        self.assertEqual(
            action["views"][0][0],
            self.env.ref("stock_return_request.view_stock_return_request_form").id,
        )
        self.assertEqual(
            action["context"]["default_partner_id"], self.so_1.partner_id.id
        )
        self.assertEqual(
            len(action["context"]["default_line_ids"]), len(returnable_lines)
        )
