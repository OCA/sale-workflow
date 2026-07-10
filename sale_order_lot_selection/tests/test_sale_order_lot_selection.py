# © 2015 Agile Business Group
# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLotSelection(BaseCommon):
    @classmethod
    def setUpClass(cls):
        """
        Set up a sale order a particular lot.

        I confirm it, transfer the delivery order and check lot on picking

        Set up a sale order with two lines with different products and lots.

        I confirm it, transfer the delivery order and check lots on picking

        """
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner Test",
            }
        )
        cls.prd_cable = cls.env["product.product"].create(
            {
                "name": "Cable Test",
                "tracking": "lot",
                "is_storable": True,
            }
        )
        cls.product_46 = cls.env["product.product"].create(
            {
                "name": "Product 46",
                "is_storable": True,
            }
        )
        cls.product_12 = cls.env["product.product"].create(
            {
                "name": "Product 12",
                "is_storable": True,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product_model = cls.env["product.product"]
        cls.lot_model = cls.env["stock.lot"]
        cls.lot_cable = cls.env["stock.lot"].create(
            {
                "name": "cable test lot",
                "product_id": cls.prd_cable.id,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.prd_cable.id,
                            "product_uom_qty": 1.0,
                            "lot_id": cls.lot_cable.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.prd_cable.id,
                            "product_uom_qty": 1.0,
                            "lot_id": cls.lot_cable.id,
                        }
                    ),
                ],
            }
        )

    def _retrieve_stock_quantity(self, product, lot, location):
        return product.with_context(lot_id=lot.id, location=location.id).qty_available

    def test_00_stock_available_wrong_lot(self):
        # We should not be able to reserve if some stock is available but with another
        # lot
        self._update_stock_quantity(self.prd_cable, self.lot_cable, 1)
        other_lot = self.env["stock.lot"].create(
            {
                "name": "test2",
                "product_id": self.prd_cable.id,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self._update_stock_quantity(self.prd_cable, other_lot, 1)
        self.sale.action_confirm()
        self.sale.picking_ids.action_assign()
        # one of 2 moves should be reserved
        available_move = self.sale.picking_ids.move_ids.filtered(
            lambda m: m.state == "assigned"
        )
        unavailable_move = self.sale.picking_ids.move_ids.filtered(
            lambda m: m.state == "confirmed"
        )
        self.assertEqual(len(available_move), 1)
        self.assertEqual(len(unavailable_move), 1)

    def _update_stock_quantity(self, product, lot, qty):
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, lot_id=lot, quantity=qty
        )

    def test_01_several_lines_with_same_lot(self):
        """You may want split your order in several lines
        even if lot/product are the same
        use cases: price is different or any shipping information
        """
        self._update_stock_quantity(self.prd_cable, self.lot_cable, 10)
        self.sale.action_confirm()

    def test_02_sale_order_lot_selection(self):
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
        picking_out._action_done()

        self.product_46.write({"tracking": "lot", "is_storable": True})
        self.product_12.write({"tracking": "lot", "is_storable": True})

        # make products enter
        picking_in = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": self.prd_cable.id,
                "product_uom_qty": 1,
                "product_uom": self.prd_cable.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
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
                "product_id": self.product_46.id,
                "product_uom_qty": 2,
                "product_uom": self.product_46.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        for move in picking_in.move_ids:
            self.assertEqual(move.state, "draft", "Wrong state of move line.")
        picking_in.action_confirm()
        for move in picking_in.move_ids:
            self.assertEqual(move.state, "assigned", "Wrong state of move line.")
        lot10 = False
        lot11 = False
        lot12 = False
        for move in picking_in.move_ids:
            if move.product_id == self.prd_cable:
                lot10 = self.lot_model.create(
                    {
                        "name": "0000010",
                        "product_id": self.prd_cable.id,
                        "product_qty": move.product_qty,
                        "company_id": self.env.company.id,
                    }
                )
                move.move_line_ids.write(
                    {"lot_id": lot10.id, "quantity": move.product_qty}
                )
            if move.product_id == self.product_46:
                lot11 = self.lot_model.create(
                    {
                        "name": "0000011",
                        "product_id": self.product_46.id,
                        "product_qty": move.product_qty,
                        "company_id": self.env.company.id,
                    }
                )
                move.move_line_ids.write(
                    {"lot_id": lot11.id, "quantity": move.product_qty}
                )
            if move.product_id == self.product_12:
                lot12 = self.lot_model.create(
                    {
                        "name": "0000012",
                        "product_id": self.product_12.id,
                        "product_qty": move.product_qty,
                        "company_id": self.env.company.id,
                    }
                )
                move.move_line_ids.write(
                    {"lot_id": lot12.id, "quantity": move.product_qty}
                )
        picking_in.button_validate()

        # check quantities
        lot10_qty_available = self._retrieve_stock_quantity(
            self.prd_cable, lot10, self.stock_location
        )
        self.assertEqual(lot10_qty_available, 1)
        lot11_qty_available = self._retrieve_stock_quantity(
            self.product_46, lot11, self.stock_location
        )
        self.assertEqual(lot11_qty_available, 2)
        lot12_qty_available = self._retrieve_stock_quantity(
            self.product_12, lot12, self.stock_location
        )
        self.assertEqual(lot12_qty_available, 1)

        # create order
        self.order1 = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.sol1 = self.env["sale.order.line"].create(
            {
                "name": "sol1",
                "order_id": self.order1.id,
                "lot_id": lot10.id,
                "product_id": self.prd_cable.id,
                "product_uom_qty": 1,
            }
        )
        self.order2 = self.env["sale.order"].create({"partner_id": self.partner.id})
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
        self.order3 = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.sol3 = self.env["sale.order.line"].create(
            {
                "name": "sol_test_1",
                "order_id": self.order3.id,
                "lot_id": lot10.id,
                "product_id": self.prd_cable.id,
                "product_uom_qty": 1,
            }
        )
        self.order4 = self.env["sale.order"].create({"partner_id": self.partner.id})
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

        picking_move_line_ids = picking.move_ids[0].move_line_ids
        picking_move_line_ids[0].quantity = 1
        picking_move_line_ids[0].location_id = self.stock_location
        picking.button_validate()

        # put back the lot because it is removed by onchange
        self.sol3.lot_id = lot10.id
        # I'll try to confirm it to check lot reservation:
        # lot10 was delivered by order1
        lot10_qty_available = self._retrieve_stock_quantity(
            self.prd_cable, lot10, self.stock_location
        )
        self.order3.action_confirm()
        self.assertEqual(self.order3.state, "sale")
        # products are not available for reservation (lot unavailable)
        self.assertEqual(self.order3.picking_ids[0].state, "confirmed")

        # onchange remove lot_id, we put it back
        self.sol2a.lot_id = lot11.id
        self.order2.action_confirm()
        picking = self.order2.picking_ids
        picking.action_assign()

        picking.move_ids.mapped("move_line_ids").write({"quantity": 1})
        picking.button_validate()

        # check quantities
        lot10_qty_available = self._retrieve_stock_quantity(
            self.prd_cable, lot10, self.stock_location
        )
        self.assertEqual(lot10_qty_available, 0)
        lot11_qty_available = self._retrieve_stock_quantity(
            self.product_46, lot11, self.stock_location
        )
        self.assertEqual(lot11_qty_available, 1)
        lot12_qty_available = self._retrieve_stock_quantity(
            self.product_12, lot12, self.stock_location
        )
        self.assertEqual(lot12_qty_available, 0)
        # I'll try to confirm it to check lot reservation:
        # lot11 has 1 availability and order4 has quantity 2
        self.order4.action_confirm()
        self.assertEqual(self.order4.state, "sale")
        # products are reserved
        self.assertEqual(self.order4.picking_ids[0].state, "assigned")

    @mute_logger("odoo.models.unlink")
    def test_03_sale_order_lot_selection_exception(self):
        self._update_stock_quantity(self.prd_cable, self.lot_cable, 2)
        lot_extra_1 = self.env["stock.lot"].create(
            {
                "name": "test lot extra 1",
                "product_id": self.prd_cable.id,
            }
        )
        self._update_stock_quantity(self.prd_cable, lot_extra_1, 1)
        lot_extra_2 = self.env["stock.lot"].create(
            {
                "name": "test lot extra 2",
                "product_id": self.prd_cable.id,
            }
        )
        self.sale.action_confirm()
        line_0 = self.sale.order_line[0]
        line_1 = self.sale.order_line[1]
        self.assertEqual(line_0.move_ids.state, "assigned")
        self.assertEqual(line_0.move_ids.restrict_lot_id, self.lot_cable)
        self.assertEqual(line_1.move_ids.restrict_lot_id, self.lot_cable)
        line_0.lot_id = lot_extra_1
        self.assertEqual(line_0.move_ids.state, "assigned")
        self.assertEqual(line_0.move_ids.restrict_lot_id, lot_extra_1)
        picking = self.sale.picking_ids
        picking.move_ids.mapped("move_line_ids").write({"quantity": 1})
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        msg = (
            "You can't modify the Lot/Serial number "
            "because some stock move has already been done."
        )
        with self.assertRaisesRegex(ValidationError, msg):
            line_0.lot_id = lot_extra_2

    def test_04_sale_order_lot_selection_confirm_lot_qty_check(self):
        self.prd_cable.tracking = "serial"
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.prd_cable.id,
                            "product_uom_qty": 1.0,
                            "lot_id": self.lot_cable.id,
                        }
                    ),
                ],
            }
        )
        # The order cannot be processed if lot is out of stock
        with self.assertRaisesRegex(
            UserError,
            "The serial number cable test lot is not available",
        ):
            sale.action_confirm()
        # Update lot quantity and confirm
        self._update_stock_quantity(self.prd_cable, self.lot_cable, 1)
        sale.action_confirm()
        self.assertEqual(sale.state, "sale")
        # Create an additional order linked to the same lot
        sale_extra = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.prd_cable.id,
                            "product_uom_qty": 1.0,
                            "lot_id": self.lot_cable.id,
                        }
                    ),
                ],
            }
        )
        # We cannot confirm the additional order if lot is out of stock
        with self.assertRaisesRegex(
            UserError,
            "The serial number cable test lot is not available",
        ):
            sale_extra.action_confirm()
        # Create an additional lot and linked it to the order
        lot_cable_extra = self.env["stock.lot"].create(
            {
                "name": "cable test lot extra",
                "product_id": self.prd_cable.id,
            }
        )
        sale_extra.order_line.lot_id = lot_cable_extra
        with self.assertRaisesRegex(
            UserError,
            "The serial number cable test lot extra is not available",
        ):
            sale_extra.action_confirm()
        # Update lot quantity and confirm
        self._update_stock_quantity(self.prd_cable, lot_cable_extra, 1)
        sale_extra.action_confirm()
        self.assertEqual(sale_extra.state, "sale")

    def test_05_available_lots_reserved_qty(self):
        """Test that reserved quantities are not included in available lots"""
        self.product_12.write({"tracking": "lot"})
        lot_demo = self.env["stock.lot"].create(
            {
                "name": "lot_reserved_test",
                "product_id": self.product_12.id,
                "company_id": self.env.company.id,
            }
        )
        self._update_stock_quantity(self.product_12, lot_demo, 10.0)

        # Create another SO and confirm it to reserve 4.0 units
        so_reserve = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_12.id,
                            "product_uom_qty": 4.0,
                            "lot_id": lot_demo.id,
                        }
                    ),
                ],
            }
        )
        so_reserve.action_confirm()
        so_reserve.picking_ids.action_assign()
        # Ensure picking is assigned so it actually reserves the quantity
        self.assertEqual(so_reserve.picking_ids[0].state, "assigned")

        # Now test the available quantities on a new draft SO
        so_new = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_12.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                ],
            }
        )
        line_new = so_new.order_line

        # Check available lots logic
        lot_info = line_new.get_available_lots_for_line()
        # The lot `lot_demo` should show 6.0 qty
        lot_res = next(
            (lot for lot in lot_info["available"] if lot["id"] == lot_demo.id), None
        )
        self.assertTrue(lot_res)
        self.assertEqual(lot_res["qty"], 6.0)

    def test_06_compute_lot_id_multi_warehouse(self):
        """A lot with stock in WH1 but not in WH2 must only be kept on the
        lines of WH1, even when both lines are recomputed in the same batch.
        """
        wh1 = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        wh2 = self.env["stock.warehouse"].create({"name": "Warehouse 2", "code": "WH2"})
        # One single lot, with stock ONLY in WH1, nothing in WH2
        self._update_stock_quantity(self.prd_cable, self.lot_cable, 10.0)

        def _make_line(warehouse):
            order = self.env["sale.order"].create(
                {
                    "partner_id": self.partner.id,
                    "warehouse_id": warehouse.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.prd_cable.id,
                                "product_uom_qty": 1.0,
                                "lot_id": self.lot_cable.id,
                            }
                        )
                    ],
                }
            )
            return order.order_line

        line_wh1 = _make_line(wh1)
        line_wh2 = _make_line(wh2)
        line_wh1.lot_id = self.lot_cable
        line_wh2.lot_id = self.lot_cable

        # Recompute both lines in a single batch
        (line_wh1 + line_wh2)._compute_lot_id()

        self.assertEqual(
            line_wh1.lot_id,
            self.lot_cable,
            "WH1 line has stock for the lot -> must be kept",
        )
        self.assertFalse(
            line_wh2.lot_id,
            "WH2 line has no stock for the lot -> must be dropped",
        )
