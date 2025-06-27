# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSOLineMultiwarehouse(TransactionCase):

    # Distribution of products in warehouses
    QUANTITIES = {
        "YourCompany": {
            "Product-1": 5,
            "Product-2": 8,
        },
        "Alternative Warehouse-1": {
            "Product-1": 6,
            "Product-2": 9,
        },
        "Alternative Warehouse-2": {
            "Product-1": 7,
            "Product-2": 10,
        },
    }

    # Distribution of quantity in used order line
    SPLIT_QTY = {
        "Product-1": {
            "YourCompany": 1,
            "Alternative Warehouse-1": 1,
            "Alternative Warehouse-2": 1,
        },
        "Product-2": {
            "YourCompany": 2,
            "Alternative Warehouse-1": 2,
            "Alternative Warehouse-2": 1,
        },
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.allow_sale_multi_warehouse = True
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.alternative_warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Alternative Warehouse-1",
                "code": "AW_1",
                "company_id": cls.company.id,
            }
        )
        cls.alternative_warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Alternative Warehouse-2",
                "code": "AW_2",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.alternative_warehouse_ids = [
            cls.alternative_warehouse_1.id,
            cls.alternative_warehouse_2.id,
        ]
        cls.product_1, cls.product_2 = cls.env["product.product"].create(
            [
                {"name": "Product-1", "detailed_type": "product"},
                {"name": "Product-2", "detailed_type": "product"},
            ]
        )

        # 5 units of product_1 in warehouse
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.warehouse.lot_stock_id, 5
        )
        # 6 units of product_1 in alternative_warehouse_1
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.alternative_warehouse_1.lot_stock_id, 6
        )
        # 7 units of product_1 in alternative_warehouse_2
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.alternative_warehouse_2.lot_stock_id, 7
        )

        # 8 units of product_1 in warehouse
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.warehouse.lot_stock_id, 8
        )
        # 9 units of product_1 in alternative_warehouse_1
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.alternative_warehouse_1.lot_stock_id, 9
        )
        # 10 units of product_1 in alternative_warehouse_2
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.alternative_warehouse_2.lot_stock_id, 10
        )

    def create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 3,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 5,
                        },
                    ),
                ],
            }
        )

    def split_order_lines(self, sale):
        # First order line split in warehouses
        #   1u. -> warehouse
        #   1u. -> alternative_warehouse_1
        #   1u. -> anternative_warehouse_2
        first_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_1
        )
        first_ol_warehouse_line = first_order_line.filtered(
            lambda a: a.warehouse_id == self.warehouse
        )
        first_ol_warehouse_line.product_uom_qty = 1
        first_order_line.write(
            {
                "sale_order_line_warehouse_ids": [
                    (
                        0,
                        0,
                        {
                            "order_line_id": first_order_line.id,
                            "product_uom_qty": 1,
                            "warehouse_id": self.alternative_warehouse_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "order_line_id": first_order_line.id,
                            "product_uom_qty": 1,
                            "warehouse_id": self.alternative_warehouse_2.id,
                        },
                    ),
                ],
            }
        )

        # Second order line split in warehouses
        #   2u. -> warehouse
        #   2u. -> alternative_warehouse_1
        #   1u. -> anternative_warehouse_2
        second_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_2
        )
        second_ol_warehouse_line = second_order_line.filtered(
            lambda a: a.warehouse_id == self.warehouse
        )
        second_ol_warehouse_line.product_uom_qty = 2
        second_order_line.write(
            {
                "sale_order_line_warehouse_ids": [
                    (
                        0,
                        0,
                        {
                            "order_line_id": second_order_line.id,
                            "product_uom_qty": 2,
                            "warehouse_id": self.alternative_warehouse_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "order_line_id": second_order_line.id,
                            "product_uom_qty": 1,
                            "warehouse_id": self.alternative_warehouse_2.id,
                        },
                    ),
                ],
            }
        )

    def test_use_only_default_warehouse(self):
        # Create sale order
        sale = self.create_sale_order()
        # Sale general values
        self.assertTrue(sale.allow_sale_multi_warehouse)
        self.assertEqual(len(sale.suitable_warehouse_ids), 3)
        self.assertEqual(sale.warehouse_id, self.warehouse)

        # First order line check
        first_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertEqual(len(first_order_line.sale_order_line_warehouse_ids), 1)
        self.assertEqual(first_order_line.qty_assigned_to_warehouse, 3)
        warehouse_line_1 = first_order_line.sale_order_line_warehouse_ids
        self.assertEqual(warehouse_line_1.product_uom_qty, 3)
        self.assertEqual(warehouse_line_1.warehouse_id, self.warehouse)
        # There are 5 units of product_1 in warehouse
        self.assertEqual(warehouse_line_1.qty_forecast, 5)
        self.assertEqual(warehouse_line_1.qty_delivered, 0)

        # Second order line check
        second_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertEqual(len(second_order_line.sale_order_line_warehouse_ids), 1)
        self.assertEqual(second_order_line.qty_assigned_to_warehouse, 5)
        warehouse_line_2 = second_order_line.sale_order_line_warehouse_ids
        self.assertEqual(warehouse_line_2.product_uom_qty, 5)
        self.assertEqual(warehouse_line_2.warehouse_id, self.warehouse)
        # There are 8 units of product_1 in warehouse
        self.assertEqual(warehouse_line_2.qty_forecast, 8)
        self.assertEqual(warehouse_line_2.qty_delivered, 0)

        # Confirm sale order
        sale.action_confirm()
        # Only 1 picking created
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        # Check picking values
        self.assertEqual(picking.location_id.warehouse_id, self.warehouse)
        self.assertEqual(len(picking.move_ids), 2)
        # Check stock moves
        product_1_move = picking.move_ids.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertTrue(len(product_1_move), 1)
        self.assertEqual(product_1_move.product_uom_qty, 3)
        product_2_move = picking.move_ids.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertTrue(len(product_2_move), 1)
        self.assertEqual(product_2_move.product_uom_qty, 5)

        # Validate picking
        product_1_move.quantity_done = 3
        product_2_move.quantity_done = 5
        picking._action_done()

        # Check sale order delivered quantity
        self.assertEqual(first_order_line.qty_delivered, 3)
        self.assertEqual(warehouse_line_1.qty_delivered, 3)
        self.assertEqual(second_order_line.qty_delivered, 5)
        self.assertEqual(warehouse_line_2.qty_delivered, 5)

    def test_split_warehouse_no_backorder(self):
        # Create sale order
        sale = self.create_sale_order()

        # Create warehouse distribution lines
        self.split_order_lines(sale)
        first_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertEqual(len(first_order_line.sale_order_line_warehouse_ids), 3)
        second_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertEqual(len(second_order_line.sale_order_line_warehouse_ids), 3)

        # Confirm sale order
        sale.action_confirm()
        # 3 pickings created
        self.assertEqual(len(sale.picking_ids), 3)

        # Check warehouse picking values
        picking_warehouse = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.warehouse
        )
        self.assertEqual(len(picking_warehouse), 1)
        self.assertEqual(len(picking_warehouse.move_ids), 2)
        # Check warehouse stock moves
        product_1_move = picking_warehouse.move_ids.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertTrue(len(product_1_move), 1)
        self.assertEqual(product_1_move.product_uom_qty, 1)
        product_2_move = picking_warehouse.move_ids.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertTrue(len(product_2_move), 1)
        self.assertEqual(product_2_move.product_uom_qty, 2)

        # Check alternative_warehouse_1 picking values
        picking_alternative_warehouse_1 = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.alternative_warehouse_1
        )
        self.assertEqual(len(picking_alternative_warehouse_1), 1)
        self.assertEqual(len(picking_alternative_warehouse_1.move_ids), 2)
        # Check alternative_warehouse_1 stock moves
        product_1_move = picking_alternative_warehouse_1.move_ids.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertTrue(len(product_1_move), 1)
        self.assertEqual(product_1_move.product_uom_qty, 1)
        product_2_move = picking_alternative_warehouse_1.move_ids.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertTrue(len(product_2_move), 1)
        self.assertEqual(product_2_move.product_uom_qty, 2)

        # Check alternative_warehouse_2 picking values
        alternative_warehouse_2 = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.alternative_warehouse_2
        )
        self.assertEqual(len(alternative_warehouse_2), 1)
        self.assertEqual(len(alternative_warehouse_2.move_ids), 2)
        # Check alternative_warehouse_2 stock moves
        product_1_move = alternative_warehouse_2.move_ids.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertTrue(len(product_1_move), 1)
        self.assertEqual(product_1_move.product_uom_qty, 1)
        product_2_move = alternative_warehouse_2.move_ids.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertTrue(len(product_2_move), 1)
        self.assertEqual(product_2_move.product_uom_qty, 1)

        # Validate pickings
        for move in sale.picking_ids.mapped("move_ids"):
            move.quantity_done = move.product_uom_qty
        sale.picking_ids._action_done()

        # Check all quantities delivered in sale order lines
        for line in sale.order_line:
            self.assertEqual(line.product_uom_qty, line.qty_delivered)

        # Check all quantities delivered in warehouse distribution lines
        for warehouse_line in sale.order_line.mapped("sale_order_line_warehouse_ids"):
            self.assertEqual(
                warehouse_line.product_uom_qty, warehouse_line.qty_delivered
            )

    def test_split_warehouse_with_backorder(self):
        # Create sale order
        sale = self.create_sale_order()

        # Create warehouse distribution lines
        self.split_order_lines(sale)

        # Confirm sale order
        sale.action_confirm()

        # Deliver all quantities in warehouse picking
        picking_warehouse = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.warehouse
        )
        for move in picking_warehouse.move_ids:
            move.quantity_done = move.product_uom_qty
        picking_warehouse._action_done()

        # Deliver all quantities in alternative_warehouse_2 picking
        picking_alternative_warehouse_2 = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.alternative_warehouse_2
        )
        for move in picking_alternative_warehouse_2.move_ids:
            move.quantity_done = move.product_uom_qty
        picking_alternative_warehouse_2._action_done()

        # Only deliver 1 unit of product_2 in alternative_warehouse_1 picking
        # Create backorder
        picking_alternative_warehouse_1 = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.alternative_warehouse_1
        )
        move = picking_alternative_warehouse_1.move_ids.filtered(
            lambda a: a.product_id == self.product_1
        )
        move.quantity_done = move.product_uom_qty
        move = picking_alternative_warehouse_1.move_ids.filtered(
            lambda a: a.product_id == self.product_2
        )
        move.quantity_done = 1
        picking_alternative_warehouse_1._action_done()
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking_alternative_warehouse_1.id)]
        )
        self.assertTrue(backorder)

        # All quantity of product_1 delivered
        product_1_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_1
        )
        self.assertEqual(
            product_1_order_line.qty_delivered, product_1_order_line.product_uom_qty
        )
        for warehouse_line in product_1_order_line.sale_order_line_warehouse_ids:
            self.assertEqual(
                warehouse_line.qty_delivered, warehouse_line.product_uom_qty
            )

        # Product_uom_qty - 1 of product_2 delivered
        product_2_order_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_2
        )
        self.assertEqual(
            product_2_order_line.qty_delivered, product_2_order_line.product_uom_qty - 1
        )
        for (
            warehouse_line
        ) in product_2_order_line.sale_order_line_warehouse_ids.filtered(
            lambda a: a.warehouse_id != self.alternative_warehouse_1
        ):
            self.assertEqual(
                warehouse_line.qty_delivered, warehouse_line.product_uom_qty
            )
        undelivered_line = product_2_order_line.sale_order_line_warehouse_ids.filtered(
            lambda a: a.warehouse_id == self.alternative_warehouse_1
        )
        self.assertEqual(len(undelivered_line), 1)
        self.assertEqual(
            undelivered_line.qty_delivered, undelivered_line.product_uom_qty - 1
        )

        # Delivery backorder
        for move in backorder.move_ids:
            move.quantity_done = move.product_uom_qty
        backorder._action_done()

        # Check all quantity has been delivered in product_2 sale order line
        self.assertEqual(
            product_2_order_line.qty_delivered, product_2_order_line.product_uom_qty
        )
        for warehouse_line in product_2_order_line.sale_order_line_warehouse_ids:
            self.assertEqual(
                warehouse_line.qty_delivered, warehouse_line.product_uom_qty
            )

    def test_extra_order_line(self):
        # Create sale order
        sale = self.create_sale_order()

        # Create warehouse distribution lines
        self.split_order_lines(sale)

        # Validate sale order
        sale.action_confirm()

        # Validate pickings
        for move in sale.picking_ids.mapped("move_ids"):
            move.quantity_done = move.product_uom_qty
        sale.picking_ids._action_done()

        # Add a new order line to the sale order
        # The new order line distributes quantity in 3 warehouses
        #   warehouse: 1u
        #   alternative_warehouse_1: 2u
        #   alternative_warehouse_2: 3u
        sale.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 1,
                        },
                    )
                ]
            }
        )
        new_line = sale.order_line.filtered(lambda a: a.qty_delivered == 0.0)
        new_line.write(
            {
                "sale_order_line_warehouse_ids": [
                    (
                        0,
                        0,
                        {
                            "product_uom_qty": 2,
                            "warehouse_id": self.alternative_warehouse_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_uom_qty": 3,
                            "warehouse_id": self.alternative_warehouse_2.id,
                        },
                    ),
                ]
            }
        )
        self.assertEqual(new_line.product_uom_qty, 6)
        self.assertEqual(new_line.qty_delivered, 0)

        # 3 new pickings have been generated by adding a new sale order line
        self.assertEqual(len(sale.picking_ids), 6)
        new_pickings = sale.picking_ids.filtered(lambda a: a.state != "done")
        self.assertEqual(len(new_pickings), 3)

        # Check qty. delivered in new warehouse distribution lines
        for wareuse_line in new_line.sale_order_line_warehouse_ids:
            self.assertEqual(wareuse_line.qty_delivered, 0)

        # Validate new pickings
        for move in new_pickings.mapped("move_ids"):
            move.quantity_done = move.product_uom_qty
        new_pickings._action_done()

        # Check quantity delivered
        self.assertEqual(new_line.qty_delivered, new_line.product_uom_qty)
        for wareuse_line in new_line.sale_order_line_warehouse_ids:
            self.assertEqual(wareuse_line.qty_delivered, wareuse_line.product_uom_qty)

    def test_extra_picking_line(self):
        # Create sale order
        sale = self.create_sale_order()

        # Create warehouse distribution lines
        self.split_order_lines(sale)

        # Validate sale order
        sale.action_confirm()

        # Add a stock move of product_1 in the alternative_warehouse_1 picking
        # (2 units)
        picking_alternative_warehouse_1 = sale.picking_ids.filtered(
            lambda a: a.location_id.warehouse_id == self.alternative_warehouse_1
        )
        new_move = self.env["stock.move"].create(
            {
                "name": self.product_1.name,
                "picking_id": picking_alternative_warehouse_1.id,
                "product_id": self.product_1.id,
                "location_id": picking_alternative_warehouse_1.move_ids[
                    0
                ].location_id.id,
                "location_dest_id": picking_alternative_warehouse_1.move_ids[
                    0
                ].location_dest_id.id,
                "quantity_done": 2,
            }
        )
        self.assertTrue(new_move)
        # Set all quantities to done and confirm picking
        for move in picking_alternative_warehouse_1.move_ids.filtered(
            lambda a: a.id != new_move.id
        ):
            move.quantity_done = move.product_uom_qty
        picking_alternative_warehouse_1._action_done()

        # A new product_1 sale order line has been automatically created
        # Check the following
        #   - This line is related to the new stock move
        #   - The new sale order line contains a warehouse distribution
        #       line related to alternative_warehouse_1
        #   - Delivered quantity in both the sale order line and the warehouse
        #       distribution line equal the quantity set in the new move.
        #   - Product quantity in both the sale order line and the warehouse
        #       distribution line equal 0.
        new_move_so_line = new_move.sale_line_id
        self.assertTrue(new_move_so_line)
        self.assertEqual(new_move_so_line.order_id, sale)
        self.assertEqual(len(new_move_so_line.sale_order_line_warehouse_ids), 1)
        new_move_so_warehouse_line = (
            new_move_so_line.sale_order_line_warehouse_ids.filtered(
                lambda a: a.warehouse_id == self.alternative_warehouse_1
            )
        )
        self.assertTrue(new_move_so_warehouse_line)
        self.assertEqual(new_move_so_line.qty_delivered, new_move.quantity_done)
        self.assertEqual(new_move_so_line.product_uom_qty, 0)
        self.assertEqual(
            new_move_so_warehouse_line.qty_delivered, new_move.quantity_done
        )
        self.assertEqual(new_move_so_warehouse_line.product_uom_qty, 0)

    def test_sync_quantity_no_pickings(self):
        # Create sale order
        sale = self.create_sale_order()

        # Create warehouse distribution lines
        self.split_order_lines(sale)

        # Test is performed over product_1 sale order line in warehouse
        # Sale order is not validated and no pickings have been created
        product_1_so_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_1
        )

        # Quantity in sale order line is increased -> Sale order warehouse
        # distribution line related to the sale order line warehouse is increased
        so_warehouse = sale.warehouse_id
        warehouse_distribution_line = (
            product_1_so_line.sale_order_line_warehouse_ids.filtered(
                lambda a: a.warehouse_id == so_warehouse
            )
        )
        product_1_so_line.product_uom_qty = 4
        self.assertEqual(warehouse_distribution_line.product_uom_qty, 2)

        # Quantity in sale order line is decreased -> Sale order warehouse
        # distribution line related to the sale order line warehouse is decreased
        product_1_so_line.product_uom_qty = 3
        self.assertEqual(warehouse_distribution_line.product_uom_qty, 1)

        # Quantity in sale order line is decreased -> Sale order warehouse
        # distribution line is deleted (as not quantity remains)
        product_1_so_line.write({"product_uom_qty": 2})
        warehouse_distribution_line = (
            product_1_so_line.sale_order_line_warehouse_ids.filtered(
                lambda a: a.warehouse_id == so_warehouse
            )
        )
        self.assertFalse(warehouse_distribution_line)

        # Quantity in sale order line is increased -> Sale order warehouse
        # distribution line is 1 (it cannot be deleted as it has a related stock move)
        product_1_so_line.write({"product_uom_qty": 3})
        warehouse_distribution_line = (
            product_1_so_line.sale_order_line_warehouse_ids.filtered(
                lambda a: a.warehouse_id == so_warehouse
            )
        )
        self.assertEqual(warehouse_distribution_line.product_uom_qty, 1)

        # Quantity in sale order line is increased -> Only 1 warehouse
        # distrubution lines remains
        product_1_so_line.write({"product_uom_qty": 1})
        self.assertEqual(len(product_1_so_line.sale_order_line_warehouse_ids), 1)

    def test_sync_quantity_with_pickings(self):
        # Create sale order
        sale = self.create_sale_order()

        # Create warehouse distribution lines
        self.split_order_lines(sale)

        # Validate sale
        sale.action_confirm()

        # Test is performed over product_1 sale order line in alternative_warehouse_1
        product_1_so_line = sale.order_line.filtered(
            lambda a: a.product_id == self.product_1
        )
        warehouse_distribution_line = (
            product_1_so_line.sale_order_line_warehouse_ids.filtered(
                lambda a: a.warehouse_id == self.alternative_warehouse_1
            )
        )

        # Quantity in the sale order distribution line related to
        # alternative_warehouse_1 is increased. -> Stock move related to the
        # distribution line is increased
        warehouse_distribution_line.write({"product_uom_qty": 2})
        self.assertEqual(
            warehouse_distribution_line.move_ids[0].product_uom_qty,
            warehouse_distribution_line.product_uom_qty,
        )

        # Quantity in the sale order distribution line related to
        # alternative_warehouse_1 is decreased. -> Stock move related to the
        # distribution line is increased
        warehouse_distribution_line.write({"product_uom_qty": 1})
        self.assertEqual(
            warehouse_distribution_line.move_ids[0].product_uom_qty,
            warehouse_distribution_line.product_uom_qty,
        )
        stock_move = warehouse_distribution_line.move_ids[0]
        warehouse_distribution_line.unlink()
        self.assertEqual(stock_move.product_uom_qty, 0)
        self.assertEqual(stock_move.state, "cancel")

        # Test is performed over product_1 sale order line in alternative_warehouse_2
        # from now on.
        warehouse_distribution_line = (
            product_1_so_line.sale_order_line_warehouse_ids.filtered(
                lambda a: a.warehouse_id == self.alternative_warehouse_2
            )
        )
        # All pickings are delivered
        for move in sale.picking_ids.mapped("move_ids").filtered(
            lambda a: a.state != "cancel"
        ):
            move.quantity_done = move.product_uom_qty
        sale.picking_ids._action_done()

        # Quantity is increased in product_1 warehouse distribution line
        # related to alternative_warehouse_2.
        # A new picking related to alternative_warehouse_2 is created, as the
        # other one is already validated
        warehouse_distribution_line.write(
            {"product_uom_qty": warehouse_distribution_line.product_uom_qty + 1}
        )
        self.assertEqual(
            len(
                sale.picking_ids.filtered(
                    lambda a: a.location_id.warehouse_id == self.alternative_warehouse_2
                )
            ),
            2,
        )

        # Quantity is decreased in product_1 warehouse distribution line
        # related to alternative_warehouse_2.
        # The picking created in the previous step is cancelled.
        warehouse_distribution_line.write(
            {"product_uom_qty": warehouse_distribution_line.product_uom_qty - 1}
        )
        picking_alternative_warehouse_2_done = sale.picking_ids.filtered(
            lambda a: a.state == "done"
            and a.location_id.warehouse_id == self.alternative_warehouse_2
        )
        self.assertEqual(len(picking_alternative_warehouse_2_done), 1)
        picking_alternative_warehouse_2_cancelled = sale.picking_ids.filtered(
            lambda a: a.state == "cancel"
            and a.location_id.warehouse_id == self.alternative_warehouse_2
        )
        self.assertEqual(len(picking_alternative_warehouse_2_cancelled), 1)

    def test_restrictions(self):
        sale = self.create_sale_order()
        self.split_order_lines(sale)
        with self.assertRaises(ValidationError):
            sale.order_line[0].write(
                {
                    "sale_order_line_warehouse_ids": [
                        (
                            0,
                            0,
                            {
                                "product_uom_qty": 1,
                                "warehouse_id": self.alternative_warehouse_1.id,
                            },
                        ),
                    ],
                }
            )

    def test_multi_warehouse_change_wizard(self):
        # Create new warehuse which is not set as an alternative warehouse
        # to any other warehouse
        new_warehouse = self.env["stock.warehouse"].create(
            {
                "name": "New Warehouse",
                "code": "NW",
                "company_id": self.company.id,
            }
        )
        sale = self.create_sale_order()
        warehouse_change_wiz = (
            self.env["so.multi.warehouse.change.wizard"]
            .with_context(default_sale_order_id=sale.id)
            .create({})
        )
        warehouse_change_wiz.write({"new_warehouse_id": new_warehouse.id})

        # Warehouses are incompatible
        warehouse_change_wiz.check_incompatible()
        self.assertEqual(warehouse_change_wiz.has_incompatibilities, "yes")
        self.assertEqual(
            len(warehouse_change_wiz.so_multi_warehouse_change_line_ids),
            len(sale.order_line),
        )
        for product in sale.order_line.mapped("product_id"):
            wizard_line = (
                warehouse_change_wiz.so_multi_warehouse_change_line_ids.filtered(
                    lambda line: line.product_id == product
                )
            )
            self.assertTrue(wizard_line)
            self.assertEqual(len(wizard_line), 1)

        # Change warehouse. All warehouse lines are now related to the new warehouse
        warehouse_change_wiz.change_warehouse()
        for warehouse_line in sale.order_line.mapped("sale_order_line_warehouse_ids"):
            self.assertEqual(warehouse_line.warehouse_id, new_warehouse)

        # Validate order and try to change warehouse
        # An error is raised
        sale.action_confirm()
        warehouse_change_wiz = (
            self.env["so.multi.warehouse.change.wizard"]
            .with_context(default_sale_order_id=sale.id)
            .create({})
        )
        warehouse_change_wiz.write({"new_warehouse_id": self.warehouse.id})
        with self.assertRaises(ValidationError):
            warehouse_change_wiz.change_warehouse()

    def replenish_qty(self, product, qty, warehouse, date=False):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": warehouse.in_type_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.lot_stock_id.id,
                "scheduled_date": date,
            }
        )
        self.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "date": date,
            }
        )
        picking.action_assign()

    def test_display_widget_draft(self):
        sale = self.create_sale_order()
        self.assertEqual(sale.state, "draft")
        for line in sale.order_line:
            self.assertTrue(line.display_qty_by_warehouse_widget)

    def test_display_widget_confirmed(self):
        sale = self.create_sale_order()
        sale.action_confirm()
        self.assertTrue(sale.state in ["sale", "done"])
        for line in sale.order_line:
            self.assertTrue(line.display_qty_by_warehouse_widget)

    def test_warehouse_qty_draft(self):
        sale = self.create_sale_order()
        self.split_order_lines(sale)

        # product_1 split in warehouses
        #   1u. -> warehouse
        #   1u. -> alternative_warehouse_1
        #   1u. -> anternative_warehouse_2

        # product_2 split in warehouses
        #   2u. -> warehouse
        #   2u. -> alternative_warehouse_1
        #   1u. -> anternative_warehouse_2

        for line in sale.order_line:
            warehouses = line.qty_by_warehouse.get("warehouses")
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertFalse(forecasted_issue)
            for warehouse in warehouses:
                values = self.QUANTITIES.get(warehouse["warehouse_name"])
                self.assertTrue(values)
                self.assertEqual(
                    values.get(line.product_id.name),
                    warehouse["virtual_available_at_date"],
                )
                self.assertEqual(
                    values.get(line.product_id.name), warehouse["free_qty_today"]
                )

        # 5 extra units of product_1 in warehouse available in 7 days
        self.replenish_qty(
            self.product_1, 5, self.warehouse, datetime.now() + timedelta(days=7)
        )

        # 5 extra units of product_1 in alternative_warehouse_1 available in 7 days
        self.replenish_qty(
            self.product_1,
            5,
            self.alternative_warehouse_1,
            datetime.now() + timedelta(days=7),
        )

        # 5 extra units of product_1 in alternative_warehouse_2 available in 7 days
        self.replenish_qty(
            self.product_1,
            5,
            self.alternative_warehouse_2,
            datetime.now() + timedelta(days=7),
        )

        # 5 extra units of product_1 in warehouse available in 7 days
        self.replenish_qty(
            self.product_2, 5, self.warehouse, datetime.now() + timedelta(days=7)
        )

        # 5 extra units of product_1 in alternative_warehouse_1 available in 7 days
        self.replenish_qty(
            self.product_2,
            5,
            self.alternative_warehouse_1,
            datetime.now() + timedelta(days=7),
        )

        # 5 extra units of product_1 in alternative_warehouse_2 available in 7 days
        self.replenish_qty(
            self.product_2,
            5,
            self.alternative_warehouse_2,
            datetime.now() + timedelta(days=7),
        )

        sale.write({"commitment_date": datetime.now() + timedelta(days=10)})

        for line in sale.order_line:
            warehouses = line.qty_by_warehouse.get("warehouses")
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertFalse(forecasted_issue)
            for warehouse in warehouses:
                values = self.QUANTITIES.get(warehouse["warehouse_name"])
                self.assertTrue(values)
                self.assertEqual(
                    values.get(line.product_id.name) + 5,
                    warehouse["virtual_available_at_date"],
                )
                self.assertEqual(
                    values.get(line.product_id.name), warehouse["free_qty_today"]
                )

        # Each line of the sale order is increased 20 units
        for line in sale.order_line:
            line.write({"product_uom_qty": line.product_uom_qty + 20})
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertTrue(forecasted_issue)

        # 20 extra units of product_1 in warehouse available in 8 days
        self.replenish_qty(
            self.product_1, 20, self.warehouse, datetime.now() + timedelta(days=8)
        )

        # 20 extra units of product_1 in alternative_warehouse_1 available in 8 days
        self.replenish_qty(
            self.product_1,
            20,
            self.alternative_warehouse_1,
            datetime.now() + timedelta(days=7),
        )

        # 20 extra units of product_1 in alternative_warehouse_2 available in 8 days
        self.replenish_qty(
            self.product_1,
            20,
            self.alternative_warehouse_2,
            datetime.now() + timedelta(days=7),
        )

        # 20 extra units of product_2 in warehouse available in 8 days
        self.replenish_qty(
            self.product_2, 20, self.warehouse, datetime.now() + timedelta(days=8)
        )

        # 20 extra units of product_2 in alternative_warehouse_1 available in 8 days
        self.replenish_qty(
            self.product_2,
            20,
            self.alternative_warehouse_1,
            datetime.now() + timedelta(days=7),
        )

        # 20 extra units of product_2 in alternative_warehouse_2 available in 8 days
        self.replenish_qty(
            self.product_2,
            20,
            self.alternative_warehouse_2,
            datetime.now() + timedelta(days=7),
        )

        for line in sale.order_line:
            line._compute_qty_by_warehouse()
            warehouses = line.qty_by_warehouse.get("warehouses")
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertFalse(forecasted_issue)
            for warehouse in warehouses:
                values = self.QUANTITIES.get(warehouse["warehouse_name"])
                self.assertTrue(values)
                self.assertEqual(
                    values.get(line.product_id.name) + 25,
                    warehouse["virtual_available_at_date"],
                )
                self.assertEqual(
                    values.get(line.product_id.name), warehouse["free_qty_today"]
                )

        sale.write({"commitment_date": datetime.now()})

        for line in sale.order_line:
            warehouses = line.qty_by_warehouse.get("warehouses")
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertTrue(forecasted_issue)
            for warehouse in warehouses:
                values = self.QUANTITIES.get(warehouse["warehouse_name"])
                self.assertTrue(values)
                self.assertEqual(
                    values.get(line.product_id.name),
                    warehouse["virtual_available_at_date"],
                )
                self.assertEqual(
                    values.get(line.product_id.name), warehouse["free_qty_today"]
                )

    def test_warehouse_qty_confirmed(self):
        sale = self.create_sale_order()
        self.split_order_lines(sale)
        sale.action_confirm()

        # product_1 split in warehouses
        #   1u. -> warehouse
        #   1u. -> alternative_warehouse_1
        #   1u. -> anternative_warehouse_2

        # product_2 split in warehouses
        #   2u. -> warehouse
        #   2u. -> alternative_warehouse_1
        #   1u. -> anternative_warehouse_2

        for line in sale.order_line:
            warehouses = line.qty_by_warehouse.get("warehouses")
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertFalse(forecasted_issue)
            for warehouse in warehouses:
                qty = self.SPLIT_QTY[line.product_id.name][warehouse["warehouse_name"]]
                self.assertTrue(qty)
                self.assertEqual(qty, warehouse["qty_available_today"])
                self.assertEqual(qty, warehouse["free_qty_today"])

        # Each line of the sale order is increased 20 units
        for line in sale.order_line:
            line.write({"product_uom_qty": line.product_uom_qty + 20})

        for line in sale.order_line:
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertTrue(forecasted_issue)
            warehouses = line.qty_by_warehouse.get("warehouses")
            for warehouse in warehouses:
                warehouse_line = line.sale_order_line_warehouse_ids.filtered(
                    lambda a, w=warehouse: w["warehouse"] == a.warehouse_id.id
                )
                self.assertTrue(warehouse_line)
                if warehouse.get("will_be_fulfilled"):
                    self.assertEqual(
                        warehouse_line.product_uom_qty, warehouse["qty_available_today"]
                    )
                    self.assertEqual(
                        warehouse_line.product_uom_qty, warehouse["free_qty_today"]
                    )
                else:
                    self.assertEqual(
                        warehouse_line.product_uom_qty,
                        warehouse["qty_available_today"]
                        - warehouse["virtual_available_at_date"],
                    )
                    self.assertEqual(
                        warehouse_line.product_uom_qty,
                        warehouse["free_qty_today"]
                        - warehouse["virtual_available_at_date"],
                    )

        replenish_date = fields.Datetime.now() + timedelta(days=7)
        # 20 extra units of product_1 in warehouse available in 8 days
        self.replenish_qty(self.product_1, 20, self.warehouse, replenish_date)
        # 20 extra units of product_2 in warehouse available in 8 days
        self.replenish_qty(self.product_2, 20, self.warehouse, replenish_date)

        # It is necessary to recompute the forecast_information field in moves
        sale.order_line.mapped("move_ids")._compute_forecast_information()

        for line in sale.order_line:
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertTrue(forecasted_issue)
            warehouses = line.qty_by_warehouse.get("warehouses")
            for warehouse in warehouses:
                self.assertTrue(warehouse["will_be_fulfilled"])
                warehouse_line = line.sale_order_line_warehouse_ids.filtered(
                    lambda a, w=warehouse: w["warehouse"] == a.warehouse_id.id
                )
                self.assertTrue(warehouse_line)
                if warehouse.get("warehouse") == self.warehouse.id:
                    self.assertEqual(
                        replenish_date, warehouse["forecast_expected_date"]
                    )
                    self.assertTrue(warehouse["forecast_expected_date_str"])
                else:
                    self.assertEqual(
                        warehouse_line.product_uom_qty, warehouse["qty_available_today"]
                    )
                    self.assertEqual(
                        warehouse_line.product_uom_qty, warehouse["free_qty_today"]
                    )
                    self.assertFalse(warehouse["forecast_expected_date"])
                    self.assertFalse(warehouse["forecast_expected_date_str"])

        # Commitment date is moved forward, so quantity will be repplenished
        # by then
        sale.write({"commitment_date": datetime.now() + timedelta(days=8)})

        for line in sale.order_line:
            forecasted_issue = line.qty_by_warehouse.get("forecasted_issue")
            self.assertFalse(forecasted_issue)
            warehouses = line.qty_by_warehouse.get("warehouses")
            for warehouse in warehouses:
                warehouse_line = line.sale_order_line_warehouse_ids.filtered(
                    lambda a, w=warehouse: w["warehouse"] == a.warehouse_id.id
                )
                self.assertTrue(warehouse_line)
                if warehouse.get("warehouse") == self.warehouse.id:
                    self.assertEqual(
                        replenish_date, warehouse["forecast_expected_date"]
                    )
                    self.assertTrue(warehouse["forecast_expected_date_str"])
                    self.assertEqual(
                        self.QUANTITIES.get(warehouse["warehouse_name"]).get(
                            line.product_id.name
                        ),
                        warehouse["qty_available_today"],
                    )
                else:
                    self.assertEqual(
                        warehouse_line.product_uom_qty, warehouse["qty_available_today"]
                    )
                    self.assertEqual(
                        warehouse_line.product_uom_qty, warehouse["free_qty_today"]
                    )
                    self.assertFalse(warehouse["forecast_expected_date"])
                    self.assertFalse(warehouse["forecast_expected_date_str"])
