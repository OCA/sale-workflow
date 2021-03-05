# © 2015 Agile Business Group
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as test_common
from odoo.exceptions import UserError


class TestSaleOrderLotSelection(test_common.SingleTransactionCase):
    def setUp(self):
        """
        Set up a sale order a particular lot.

        I confirm it, transfer the delivery order and check lot on picking

        Set up a sale order with two lines with different products and lots.

        I confirm it, transfer the delivery order and check lots on picking

        """
        super(TestSaleOrderLotSelection, self).setUp()
        self.product_57 = self.env.ref("product.product_product_6").copy(
            {"type": "consu"}
        )
        self.product_57.tracking = "lot"
        self.product_46 = self.env.ref("product.product_product_13").copy(
            {"type": "consu"}
        )
        self.product_12 = self.env.ref("product.product_product_12").copy(
            {"type": "consu"}
        )
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.product_model = self.env["product.product"]
        self.production_lot_model = self.env["stock.production.lot"]

    def _stock_quantity(self, product, lot, location):
        return product.with_context(
            {"lot_id": lot.id, "location": location.id}
        ).qty_available

    def test_sale_order_lot_selection(self):
        # INIT stock of products to 0
        picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product_57.name,
                "product_id": self.product_57.id,
                "product_uom_qty": self.product_57.qty_available,
                "product_uom": self.product_57.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product_12.name,
                "product_id": self.product_12.id,
                "product_uom_qty": self.product_12.qty_available,
                "product_uom": self.product_12.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product_46.name,
                "product_id": self.product_46.id,
                "product_uom_qty": self.product_46.qty_available,
                "product_uom": self.product_46.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking_out.action_confirm()
        picking_out.action_assign()
        picking_out.action_done()

        self.product_57.write({"tracking": "lot", "type": "product"})
        self.product_46.write({"tracking": "lot", "type": "product"})
        self.product_12.write({"tracking": "lot", "type": "product"})

        # make products enter
        picking_in = self.env["stock.picking"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product_57.name,
                "product_id": self.product_57.id,
                "product_uom_qty": 1,
                "product_uom": self.product_57.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product_12.name,
                "product_id": self.product_12.id,
                "product_uom_qty": 1,
                "product_uom": self.product_12.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product_46.name,
                "product_id": self.product_46.id,
                "product_uom_qty": 2,
                "product_uom": self.product_46.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        for move in picking_in.move_lines:
            self.assertEqual(move.state, "draft", "Wrong state of move line.")
        picking_in.action_confirm()
        for move in picking_in.move_lines:
            self.assertEqual(move.state, "assigned", "Wrong state of move line.")
        lot10 = False
        lot11 = False
        lot12 = False
        for ops in picking_in.move_ids_without_package:
            if ops.product_id == self.product_57:
                lot10 = self.production_lot_model.create(
                    {
                        "name": "0000010",
                        "product_id": self.product_57.id,
                        "product_qty": ops.product_qty,
                        "company_id": self.env.company.id,
                    }
                )
                ops.move_line_ids.write(
                    {"lot_id": lot10.id, "qty_done": ops.product_qty}
                )
            if ops.product_id == self.product_46:
                lot11 = self.production_lot_model.create(
                    {
                        "name": "0000011",
                        "product_id": self.product_46.id,
                        "product_qty": ops.product_qty,
                        "company_id": self.env.company.id,
                    }
                )
                ops.move_line_ids.write(
                    {"lot_id": lot11.id, "qty_done": ops.product_qty}
                )
            if ops.product_id == self.product_12:
                lot12 = self.production_lot_model.create(
                    {
                        "name": "0000012",
                        "product_id": self.product_12.id,
                        "product_qty": ops.product_qty,
                        "company_id": self.env.company.id,
                    }
                )
                ops.move_line_ids.write(
                    {"lot_id": lot12.id, "qty_done": ops.product_qty}
                )
        picking_in.action_done()

        # check quantities
        lot10_qty_available = self._stock_quantity(
            self.product_57, lot10, self.stock_location
        )
        self.assertEqual(lot10_qty_available, 1)
        lot11_qty_available = self._stock_quantity(
            self.product_46, lot11, self.stock_location
        )
        self.assertEqual(lot11_qty_available, 2)
        lot12_qty_available = self._stock_quantity(
            self.product_12, lot12, self.stock_location
        )
        self.assertEqual(lot12_qty_available, 1)

        # create order
        self.order1 = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        self.sol1 = self.env["sale.order.line"].create(
            {
                "name": "sol1",
                "order_id": self.order1.id,
                "lot_id": lot10.id,
                "product_id": self.product_57.id,
                "product_uom_qty": 1,
            }
        )
        self.order2 = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        self.sol2a = self.env["sale.order.line"].create(
            {
                "name": "sol2a",
                "order_id": self.order2.id,
                "lot_id": lot11.id,
                "product_id": self.product_46.id,
                "product_uom_qty": 1,
            }
        )
        self.sol2b = self.env["sale.order.line"].create(
            {
                "name": "sol2b",
                "order_id": self.order2.id,
                "lot_id": lot12.id,
                "product_id": self.product_12.id,
                "product_uom_qty": 1,
            }
        )
        self.order3 = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        self.sol3 = self.env["sale.order.line"].create(
            {
                "name": "sol_test_1",
                "order_id": self.order3.id,
                "lot_id": lot10.id,
                "product_id": self.product_57.id,
                "product_uom_qty": 1,
            }
        )
        self.order4 = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        self.sol4 = self.env["sale.order.line"].create(
            {
                "name": "sol4",
                "order_id": self.order4.id,
                "lot_id": lot11.id,
                "product_id": self.product_46.id,
                "product_uom_qty": 2,
            }
        )

        # confirm orders
        self.order1.action_confirm()
        picking = self.order1.picking_ids

        picking_move_line_ids = picking.move_ids_without_package[0].move_line_ids
        picking_move_line_ids[0].qty_done = 1
        picking_move_line_ids[0].location_id = self.stock_location
        picking.button_validate()

        onchange_res = self.sol3._onchange_product_id_set_lot_domain()
        self.assertEqual(onchange_res["domain"]["lot_id"], [("id", "in", [])])
        # put back the lot because it is removed by onchange
        self.sol3.lot_id = lot10.id
        # I'll try to confirm it to check lot reservation:
        # lot10 was delivered by order1
        with self.assertRaises(UserError):
            self.order3.action_confirm()

        # also test on_change for order2
        onchange_res = self.sol2a._onchange_product_id_set_lot_domain()
        self.assertEqual(onchange_res["domain"]["lot_id"], [("id", "in", [lot11.id])])
        # onchange remove lot_id, we put it back
        self.sol2a.lot_id = lot11.id
        self.order2.action_confirm()
        picking = self.order2.picking_ids
        picking.action_assign()

        picking.move_ids_without_package.mapped("move_line_ids").write({"qty_done": 1})
        picking.button_validate()

        # check quantities
        lot10_qty_available = self._stock_quantity(
            self.product_57, lot10, self.stock_location
        )
        self.assertEqual(lot10_qty_available, 0)
        lot11_qty_available = self._stock_quantity(
            self.product_46, lot11, self.stock_location
        )
        self.assertEqual(lot11_qty_available, 1)
        lot12_qty_available = self._stock_quantity(
            self.product_12, lot12, self.stock_location
        )
        self.assertEqual(lot12_qty_available, 0)
        # I'll try to confirm it to check lot reservation:
        # lot11 has 1 availability and order4 has quantity 2
        with self.assertRaises(UserError):
            self.order4.action_confirm()
