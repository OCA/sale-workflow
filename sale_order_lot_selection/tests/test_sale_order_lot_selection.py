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
                "inventory_name": self.product_12.name,
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
                "inventory_name": self.product_46.name,
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

        self.product_46.write({"tracking": "lot", "type": "consu"})
        self.product_12.write({"tracking": "lot", "type": "consu"})

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
                "inventory_name": self.prd_cable.name,
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
                "inventory_name": self.product_12.name,
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
                "inventory_name": self.product_46.name,
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

    def test_05_domain_lot_id_excludes_pending_orders_serial(self):
        """Verify that a serial number already selected in a draft quotation
        is excluded from the selection domain of other sale order lines.
        """
        # Enable the exclusion business rule
        self.env.company.write(
            {"sale_order_lot_selection_exclude_pending_orders": True}
        )

        # Ensure the product is configured with unique serial number tracking
        self.prd_cable.write({"tracking": "serial"})

        # Create a unique serial number with available stock
        serial_number = self.env["stock.lot"].create(
            {
                "name": "SN-EXCLUSIVE-001",
                "product_id": self.prd_cable.id,
                "company_id": self.env.company.id,
            }
        )
        self._update_stock_quantity(self.prd_cable, serial_number, 1)

        # Create a first order (Draft) that reserves this serial number
        order_1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": order_1.id,
                "product_id": self.prd_cable.id,
                "product_uom_qty": 1,
                "lot_id": serial_number.id,
            }
        )

        # Create a second concurrent order for the same product
        order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        sol_2 = self.env["sale.order.line"].create(
            {
                "order_id": order_2.id,
                "product_id": self.prd_cable.id,
                "product_uom_qty": 1,
            }
        )

        # Retrieve the calculated selection domain for line 2
        domain_lot_ids = []
        if sol_2.domain_lot_id:
            domain_lot_ids = [d[2] for d in sol_2.domain_lot_id if d[0] == "id"][0]

        # Business rule: The serial number from order 1 MUST be excluded
        self.assertNotIn(serial_number.id, domain_lot_ids)

    def test_06_lot_id_quant_domain_hooks(self):
        """Verify the validity of the hooks used to filter stock locations
        and build the quant search domain.
        """
        # 1. Create minimal data structure
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        sol = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prd_cable.id,
                "product_uom_qty": 5.0,  # Put a distinct quantity to test the value
            }
        )

        # 2. Test target location hook
        location = sol._get_lot_id_quant_domain_locations()
        self.assertEqual(location, sol.warehouse_id.lot_stock_id)

        # 3. Test quant domain hook (Structure and Values)
        quant_domain = sol._domain_lot_id_quant_domain()

        # Convert the domain list of tuples into a dictionary for clean assertions
        # This filters out operators like '&' or '|' automatically
        domain_dict = {
            criterion[0]: (criterion[1], criterion[2])
            for criterion in quant_domain
            if len(criterion) == 3
        }

        # Assert both keys presence and correctness of values
        self.assertEqual(domain_dict.get("product_id"), ("=", sol.product_id.id))
        self.assertEqual(domain_dict.get("quantity"), (">=", 5.0))
        self.assertEqual(domain_dict.get("location_id"), ("child_of", location.ids))
        self.assertEqual(domain_dict.get("lot_id"), ("!=", False))

    def test_selection_product_tracking_values(self):
        """Verify that the dynamic selection method correctly extracts
        the tracking options from the product model.
        """
        # 1. Call the model's selection method
        selection_options = self.env["sale.order.line"]._selection_product_tracking()

        # 2. Convert directly to a dictionary to easily extract and map keys to labels
        selection_dict = dict(selection_options)

        # 3. Assert precise presence of core Odoo tracking options as keys
        self.assertIn("serial", selection_dict)
        self.assertIn("lot", selection_dict)
        self.assertIn("none", selection_dict)
