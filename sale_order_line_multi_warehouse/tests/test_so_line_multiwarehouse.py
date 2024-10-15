# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSOLineMultiwarehouse(TransactionCase):
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
