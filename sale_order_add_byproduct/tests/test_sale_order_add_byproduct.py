# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.sale_order_add_byproduct.models.mrp_production import (
    DEFAULT_BYPRODUCT_NOTE_TEMPLATE,
)


@tagged("post_install", "-at_install")
class TestByproductToSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # --- Basic Data Setup ---
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "email": "test@example.com",
            }
        )
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.stock_location_stock = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_suppliers = cls.env.ref("stock.stock_location_suppliers")

        cls.stock_location_production = cls.env["stock.location"].search(
            [
                ("usage", "=", "production"),
                (
                    "name",
                    "=",
                    "Production",
                ),
            ],
            limit=1,
        )

        # --- Product Categories ---
        # Create a dedicated category for byproducts
        cls.byproduct_category = cls.env["product.category"].create(
            {
                "name": "By-products (Test Category)",
            }
        )

        # --- Routes ---
        cls.manufacture_route = cls.env.ref(
            "mrp.route_warehouse0_manufacture"
        )  # Manufacture route
        cls.mto_route = cls.env.ref(
            "stock.route_warehouse0_mto"
        )  # Make To Order route for automatic MO creation
        # Ensure routes are active
        cls.manufacture_route.active = True
        cls.mto_route.active = True

        # Ensure the main warehouse is properly configured for MTO
        cls.warehouse = cls.env.ref("stock.warehouse0")
        # In Odoo 18, warehouse resupply is managed directly via routes.
        # We ensure "Manufacture" is an active route and "Buy" is not.

        cls.warehouse.write({"route_ids": [(4, cls.manufacture_route.id)]})

        # --- Products ---
        cls.product_main = cls.env["product.product"].create(
            {
                "name": "Main Product X",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "uom_id": cls.product_uom_unit.id,
                "uom_po_id": cls.product_uom_unit.id,
                "route_ids": [(6, 0, [cls.manufacture_route.id, cls.mto_route.id])],
                "standard_price": 10.0,
                "lst_price": 20.0,
                "sale_ok": True,
                "purchase_ok": False,
            }
        )

        cls.product_byproduct = cls.env["product.product"].create(
            {
                "name": "By-product Y",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": cls.byproduct_category.id,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "route_ids": [
                    (6, 0, [cls.manufacture_route.id, cls.mto_route.id])
                ],  # Has manufacture route to test the blocking
                "standard_price": 1.0,
                "lst_price": 5.0,
                "sale_ok": True,
                "purchase_ok": False,
            }
        )

        cls.product_byproduct_not_sale = cls.env["product.product"].create(
            {
                "name": "By-product Z (Not Saleable)",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": cls.byproduct_category.id,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "route_ids": [(6, 0, [cls.manufacture_route.id, cls.mto_route.id])],
                "standard_price": 0.1,
                "lst_price": 0.2,
                "sale_ok": False,
                "purchase_ok": False,
            }
        )

        cls.product_component = cls.env["product.product"].create(
            {
                "name": "Component A",
                "type": "consu",
                "is_storable": True,
                # "tracking": "none",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "uom_id": cls.product_uom_unit.id,
                "uom_po_id": cls.product_uom_unit.id,
                # "route_ids": [(6, 0, [cls.buy_route.id])],  # Has buy route
                "standard_price": 5.0,
                "lst_price": 7.0,
                "sale_ok": True,
                "purchase_ok": True,
            }
        )

        cls.main_product_non_saleable_byproduct = cls.env["product.product"].create(
            {
                "name": "Main Product B (for non-saleable BP)",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "uom_id": cls.product_uom_unit.id,
                "uom_po_id": cls.product_uom_unit.id,
                "route_ids": [(6, 0, [cls.manufacture_route.id, cls.mto_route.id])],
                "standard_price": 10.0,
                "lst_price": 20.0,
                "sale_ok": True,
                "purchase_ok": False,
            }
        )

        cls.bom_non_saleable_byproduct = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.main_product_non_saleable_byproduct.product_tmpl_id.id,  # noqa
                "product_id": cls.main_product_non_saleable_byproduct.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_component.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.product_component.uom_id.id,
                        },
                    )
                ],
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_byproduct_not_sale.id,
                            "product_qty": 1.0,  # 1kg of non-saleable byproduct
                            "product_uom_id": cls.product_byproduct_not_sale.uom_id.id,  # noqa
                            "cost_share": 0,
                        },
                    )
                ],
            }
        )

        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_main.product_tmpl_id.id,
                "product_id": cls.product_main.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_component.id,
                            "product_qty": 2.0,
                            # "product_uom_id": cls.product_component.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.env["mrp.bom.byproduct"].create(
            {
                "product_id": cls.product_byproduct.id,
                "product_qty": 0.5,  # 0.5 kg of by-product per 1 main product
                "product_uom_id": cls.product_byproduct.uom_id.id,
                "bom_id": cls.bom.id,
                # "cost_share": 10,
            }
        )

        # --- Create some stock for components so MO can be marked done ---
        cls.env["stock.quant"].with_context(
            inventory_mode=True
        )._update_available_quantity(
            cls.product_component,
            cls.stock_location_stock,
            100,
        )

    def _create_and_process_mo_for_sale_order(
        self,
        main_product_qty=1.0,
        byproduct_produced_qty=0.5,
        existing_so_line_initial_qty=0.0,
        main_product_param=None,
        byproduct_product_param=None,
        bom_param=None,
    ):
        """Helper to create and process an MO related to a Sale Order,
        including optional initial SO line for byproduct."""

        # Use provided parameters or fall back to default test products
        main_product_to_use = main_product_param or self.product_main
        byproduct_product_to_use = byproduct_product_param or self.product_byproduct
        # BOM parameter is not directly used in this method but kept for
        # consistency with method signature

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": main_product_to_use.id,
                            "product_uom_qty": main_product_qty,
                            "product_uom": main_product_to_use.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

        if existing_so_line_initial_qty > 0.0:
            self.env["sale.order.line"].create(
                {
                    "order_id": sale_order.id,
                    "product_id": byproduct_product_to_use.id,
                    "product_uom_qty": existing_so_line_initial_qty,
                    "product_uom": byproduct_product_to_use.uom_id.id,
                    "is_mrp_byproduct_line": True,
                }
            )

        sale_order.action_confirm()

        mo = self.env["mrp.production"].search(
            [
                ("origin", "ilike", sale_order.name),
                ("product_id", "=", main_product_to_use.id),
            ],
            limit=1,
        )

        self.assertTrue(
            mo,
            f"MO for {main_product_to_use.name} (SO {sale_order.name}) "
            "should be created automatically when confirming the sale order.",
        )
        self.assertEqual(
            mo.product_qty,
            main_product_qty,
            "MO quantity should match main product qty.",
        )

        self.assertEqual(
            mo.state, "confirmed", "MO should be confirmed before proceeding."
        )

        # Ensure components are available for the MO.
        for bom_line in mo.bom_id.bom_line_ids:
            if bom_line.product_id == self.product_component:
                self.env["stock.quant"].with_context(
                    inventory_mode=True
                )._update_available_quantity(
                    bom_line.product_id,
                    self.stock_location_stock,
                    bom_line.product_qty * mo.product_qty + 10,  # Add a buffer
                )

        self.env.invalidate_all()
        mo = self.env["mrp.production"].browse(mo.id)

        mo.action_assign()  # Attempt to assign components.

        self.env.invalidate_all()  # Re-fetch MO state after action_assign
        mo = self.env["mrp.production"].browse(mo.id)

        if mo.state == "confirmed":
            mo.button_plan()  # Move to planned if applicable

        self.env.invalidate_all()  # Re-fetch MO state after button_plan
        mo = self.env["mrp.production"].browse(mo.id)

        # --- Simulate consumption and production ---
        # These calls should generally succeed if the MO is
        # 'confirmed' or 'assigned'
        # and stock is available.

        for move_raw in mo.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        # Update: use main_product_to_use for finished move as well
        main_finished_move = mo.move_finished_ids.filtered(
            lambda m: m.product_id == main_product_to_use
        )
        self.assertTrue(main_finished_move, "Main finished product move not found.")
        main_finished_move.quantity = main_finished_move.product_uom_qty

        byproduct_move = mo.move_byproduct_ids.filtered(
            lambda m: m.product_id == byproduct_product_to_use
        )
        self.assertTrue(byproduct_move, "By-product move not found.")
        byproduct_move.quantity = byproduct_produced_qty

        # Now process the moves
        for move_raw in mo.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        main_finished_move._action_done()
        byproduct_move._action_done()

        # Refresh the sale order to ensure all changes are reflected
        sale_order.invalidate_recordset()
        # Re-fetch to ensure fresh data
        sale_order = sale_order.browse(sale_order.id)
        return mo, sale_order

    def test_01_byproduct_added_to_sale_order_new_line(self):
        """
        Test that a new by-product line is added to the SO
        with the correct flag,
        and it does not trigger a new procurement for the by-product.
        """
        mo, sale_order = self._create_and_process_mo_for_sale_order(
            main_product_qty=1.0, byproduct_produced_qty=0.5
        )

        # Mark MO as done - this is where our custom code should trigger
        mo.button_mark_done()

        # Assert MO is done
        self.assertEqual(
            mo.state, "done", "Manufacturing order should be in 'done' state."
        )

        # Assert a new sale order line for the byproduct is created
        byproduct_so_line = sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertTrue(
            byproduct_so_line,
            "By-product line was not added to the Sale Order.",
        )
        self.assertEqual(len(byproduct_so_line), 1, "Expected one by-product line.")
        self.assertAlmostEqual(
            byproduct_so_line.product_uom_qty,
            0.5,
            places=2,
            msg="By-product quantity on SO line is incorrect.",
        )
        self.assertTrue(
            byproduct_so_line.is_mrp_byproduct_line,
            "By-product line flag is not set.",
        )

        # Assert _action_launch_stock_rule was NOT called for the byproduct line
        # from our override
        new_procurement_groups = self.env["procurement.group"].search(
            [
                ("sale_id", "=", sale_order.id),
                ("move_type", "=", "manufacture"),
                ("name", "like", f"%{self.product_byproduct.name}%"),
            ]
        )
        self.assertFalse(
            new_procurement_groups,
            "No new procurement group should be created for the byproduct "
            "after MO done.",
        )

    def test_02_byproduct_added_to_sale_order_update_existing_line(self):
        """
        Test that an existing by-product line on the SO is updated
        with the correct quantity and flag.
        """
        initial_byproduct_qty = 0.1
        mo_2, sale_order_2 = self._create_and_process_mo_for_sale_order(
            main_product_qty=1.0,
            byproduct_produced_qty=0.5,
            existing_so_line_initial_qty=initial_byproduct_qty,
        )

        # The helper creates and processes mo_2.
        # We just ensure it's a valid MO here.
        self.assertTrue(
            mo_2, "MO must be created by helper for test_02."
        )  # Ensure it's not None

        # Re-fetch the existing byproduct SO line after helper execution
        existing_byproduct_so_line = sale_order_2.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertTrue(
            existing_byproduct_so_line,
            "Existing by-product line should exist from helper.",
        )
        self.assertEqual(
            existing_byproduct_so_line.product_uom_qty,
            initial_byproduct_qty,
            "Initial by-product quantity is incorrect.",
        )

        # Mark MO as done
        mo_2.button_mark_done()

        self.assertEqual(
            mo_2.state, "done", "Manufacturing order should be in 'done' state."
        )

        # Assert the existing sale order line for the byproduct is updated
        updated_byproduct_so_line = sale_order_2.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertEqual(
            updated_byproduct_so_line.product_uom_qty,
            initial_byproduct_qty + 0.5,
            "By-product quantity was not updated correctly.",
        )
        self.assertTrue(
            updated_byproduct_so_line.is_mrp_byproduct_line,
            "By-product line flag should be true after update.",
        )

        # Check for new procurement groups
        new_procurement_groups = self.env["procurement.group"].search(
            [
                ("sale_id", "=", sale_order_2.id),
                ("move_type", "=", "manufacture"),
                ("name", "like", f"%{self.product_byproduct.name}%"),
            ]
        )
        self.assertFalse(
            new_procurement_groups,
            "No new procurement group should be created for the byproduct on update.",
        )

    def test_03_no_byproduct_transfer_without_sale_order(self):
        """
        Test that no by-products are added/updated if the MO has no associated
        Sale Order.
        """
        # Find the manufacturing picking type
        mrp_picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id", "=", self.env.ref("stock.warehouse0").id),
            ],
            limit=1,
        )
        self.assertTrue(
            mrp_picking_type,
            "Standard 'Manufacturing' picking type not found by code.",
        )

        # Create an MO not linked to any SO
        # (e.g., created directly from MRP app)
        mrp_order_no_so = self.env["mrp.production"].create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "product_uom_id": self.product_main.uom_id.id,
                "origin": False,  # Explicitly no origin
                "picking_type_id": mrp_picking_type.id,
            }
        )

        # Confirm MO and ensure components are available
        mrp_order_no_so.action_confirm()
        self.assertEqual(
            mrp_order_no_so.state,
            "confirmed",
            "MO should be confirmed after action_confirm.",
        )

        for bom_line in mrp_order_no_so.bom_id.bom_line_ids:
            if bom_line.product_id == self.product_component:
                self.env["stock.quant"].with_context(
                    inventory_mode=True
                )._update_available_quantity(
                    bom_line.product_id,
                    self.stock_location_stock,
                    bom_line.product_qty * mrp_order_no_so.product_qty + 10,
                )

        # --- REVISED MO STATE TRANSITION (removed in_progress assertion) ---
        self.env.invalidate_all()  # Clear all caches
        mrp_order_no_so = self.env["mrp.production"].browse(mrp_order_no_so.id)

        mrp_order_no_so.action_assign()

        self.env.invalidate_all()
        mrp_order_no_so = self.env["mrp.production"].browse(mrp_order_no_so.id)

        if mrp_order_no_so.state == "confirmed":
            mrp_order_no_so.button_plan()

        self.env.invalidate_all()
        mrp_order_no_so = self.env["mrp.production"].browse(mrp_order_no_so.id)

        # Removed assertion for 'in_progress' from here.

        # Simulate consumption of raw materials
        for move_raw in mrp_order_no_so.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        # Simulate production of the main finished product
        main_finished_move_no_so = mrp_order_no_so.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_main
        )
        self.assertTrue(
            main_finished_move_no_so, "Main finished product move not found."
        )
        main_finished_move_no_so.quantity = main_finished_move_no_so.product_uom_qty

        # Simulate production of the by-product
        byproduct_move_no_so = mrp_order_no_so.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_byproduct
        )
        self.assertTrue(byproduct_move_no_so, "By-product move not found.")
        byproduct_move_no_so.quantity = 0.5

        # Now process the moves
        main_finished_move_no_so._action_done()
        byproduct_move_no_so._action_done()

        # Mark the MO as done
        mrp_order_no_so.button_mark_done()

        self.assertEqual(
            mrp_order_no_so.state,
            "done",
            "Manufacturing order should be in 'done' state.",
        )

        # Assert no new Sale Order Lines were created
        # by checking the partner's sale orders
        sale_orders_for_partner = self.env["sale.order"].search(
            [("partner_id", "=", self.partner.id)]
        )

        self.assertEqual(
            len(
                sale_orders_for_partner.mapped("order_line").filtered(
                    lambda li: li.product_id == self.product_byproduct
                )
            ),
            0,
            "No by-product lines should be added to any SO for this partner if "
            "MO had no origin.",
        )

    def test_04_byproduct_line_does_not_trigger_procurement_directly(self):
        """
        Test that a sale order line explicitly marked as is_mrp_byproduct_line
        does not trigger procurement rules, even if it has a manufacture route.
        """
        # Ensure the by-product product has a 'Manufacture' route for this test
        self.assertIn(
            self.manufacture_route,
            self.product_byproduct.route_ids,
            "By-product must have manufacture route for this test to be relevant.",
        )

        current_sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_main.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_main.uom_id.id,
                        },
                    )
                ],
            }
        )
        current_sale_order.action_confirm()

        # Create a new SO line explicitly marked as a byproduct line
        so_line_byproduct = self.env["sale.order.line"].create(
            {
                "order_id": current_sale_order.id,
                "product_id": self.product_byproduct.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product_byproduct.uom_id.id,
                "is_mrp_byproduct_line": True,
            }
        )

        # --- Test the effect without patching _action_launch_stock_rule ---
        # Call the method directly.
        # Our override should prevent it from calling super with this line.
        so_line_byproduct._action_launch_stock_rule()

        # Assert no procurement group was created for this specific line
        # due to its flag
        # Re-fetch the sale order to ensure cache is cleared before searching
        # for procurement groups
        current_sale_order.invalidate_recordset()
        current_sale_order = self.env["sale.order"].browse(current_sale_order.id)

        new_procurement_groups = self.env["procurement.group"].search(
            [
                ("sale_id", "=", current_sale_order.id),
                ("move_type", "=", "manufacture"),
                ("name", "like", f"%{self.product_byproduct.name}%"),
            ]
        )
        self.assertFalse(
            new_procurement_groups,
            "No procurement group should be created for a flagged byproduct line.",
        )
        # --- End Test ---

    def test_05_byproduct_not_added_if_not_sale_ok(self):
        """
        Test that by-products are NOT added to the sale order if their
        'sale_ok' field is False.
        """
        # Use the helper to create and process the MO,
        # specifying the non-saleable by-product
        # The helper will return the MO already in a state ready
        # to be marked done, with all its moves completed.
        mo_3, sale_order_3 = self._create_and_process_mo_for_sale_order(
            main_product_qty=2.0,  # Client orders 2 units of main product B
            byproduct_produced_qty=2.0,  # 2 units produced
            main_product_param=self.main_product_non_saleable_byproduct,
            byproduct_product_param=self.product_byproduct_not_sale,
            bom_param=self.bom_non_saleable_byproduct,
        )

        # Mark the MO as done
        # (this is the key action your custom module listens to)
        mo_3.button_mark_done()

        self.assertEqual(mo_3.state, "done", "MO should be in 'done' state.")

        # Assert that the non-saleable by-product was
        # NOT added to the Sale Order
        non_saleable_byproduct_so_line = sale_order_3.order_line.filtered(
            lambda line: line.product_id == self.product_byproduct_not_sale
        )
        self.assertFalse(
            non_saleable_byproduct_so_line,
            "Non-saleable by-product should NOT be added to the Sale Order lines.",
        )

    def test_06_byproduct_respects_pricelist_price(self):
        """
        Test that by-products are added to the Sale Order with prices
        from the pricelist, not the product's list price.
        """
        # Create a pricelist with specific rules
        Pricelist = self.env["product.pricelist"]
        PricelistItem = self.env["product.pricelist.item"]

        # Change the original byproduct's list price to something different
        original_lst_price = self.product_byproduct.lst_price
        self.product_byproduct.lst_price = 5.0  # Original is 5.0 from setup

        # Create a pricelist with a specific price for the byproduct
        pricelist = Pricelist.create(
            {
                "name": "Test Byproduct Pricelist",
                "currency_id": self.env.ref("base.USD").id,
            }
        )

        # Create a pricelist item that gives the byproduct a specific price
        PricelistItem.create(
            {
                "pricelist_id": pricelist.id,
                "product_tmpl_id": self.product_byproduct.product_tmpl_id.id,
                "fixed_price": 7.5,  # Different price than lst_price
            }
        )

        # Create a sale order with this pricelist
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_main.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product_main.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()

        mo = self.env["mrp.production"].search(
            [
                ("origin", "ilike", sale_order.name),
                ("product_id", "=", self.product_main.id),
            ],
            limit=1,
        )

        self.assertTrue(
            mo,
            f"MO for {self.product_main.name} (SO {sale_order.name}) "
            "should be created automatically when confirming the sale order.",
        )

        self.assertEqual(
            mo.state, "confirmed", "MO should be confirmed before proceeding."
        )

        # Ensure components are available for the MO
        for bom_line in mo.bom_id.bom_line_ids:
            if bom_line.product_id == self.product_component:
                self.env["stock.quant"].with_context(
                    inventory_mode=True
                )._update_available_quantity(
                    bom_line.product_id,
                    self.stock_location_stock,
                    bom_line.product_qty * mo.product_qty + 10,  # Add a buffer
                )

        self.env.invalidate_all()
        mo = self.env["mrp.production"].browse(mo.id)

        mo.action_assign()

        self.env.invalidate_all()
        mo = self.env["mrp.production"].browse(mo.id)

        if mo.state == "confirmed":
            mo.button_plan()

        self.env.invalidate_all()
        mo = self.env["mrp.production"].browse(mo.id)

        # Simulate consumption and production
        for move_raw in mo.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        main_finished_move = mo.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_main
        )
        self.assertTrue(main_finished_move, "Main finished product move not found.")
        main_finished_move.quantity = main_finished_move.product_uom_qty

        byproduct_move = mo.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_byproduct
        )
        self.assertTrue(byproduct_move, "By-product move not found.")
        byproduct_move.quantity = 0.5  # 0.5 kg of byproduct

        # Process the moves
        for move_raw in mo.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        main_finished_move._action_done()
        byproduct_move._action_done()

        # Mark MO as done - this is where our custom code should trigger
        mo.button_mark_done()

        # Assert MO is done
        self.assertEqual(
            mo.state, "done", "Manufacturing order should be in 'done' state."
        )

        # Assert a new sale order line for the byproduct is created with pricelist price
        byproduct_so_line = sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertTrue(
            byproduct_so_line,
            "By-product line was not added to the Sale Order.",
        )
        self.assertEqual(len(byproduct_so_line), 1, "Expected one by-product line.")

        # Check that the price used is from the pricelist, not the product's list price
        expected_price = 7.5  # From the pricelist
        actual_price = byproduct_so_line.price_unit
        error_msg = (
            f"Price should come from the pricelist ({expected_price}), "
            f"not the product's list price ({original_lst_price}). "
            f"Actual price: {actual_price}"
        )
        self.assertEqual(actual_price, expected_price, error_msg)

    def test_08_byproduct_linked_via_origin_only(self):
        """A standalone MO whose ``origin`` matches an SO name (no procurement
        group nor sale_line_id) should still resolve the Sale Order."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_main.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product_main.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()

        mrp_picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id", "=", self.env.ref("stock.warehouse0").id),
            ],
            limit=1,
        )
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "product_uom_id": self.product_main.uom_id.id,
                "origin": sale_order.name,
                "picking_type_id": mrp_picking_type.id,
            }
        )
        # Sanity: no direct link, only origin
        self.assertFalse(mo.sale_line_id)
        self.assertFalse(mo.procurement_group_id.sale_id)

        mo.action_confirm()
        for move_raw in mo.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        main_move = mo.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_main
        )
        main_move.quantity = main_move.product_uom_qty
        main_move._action_done()

        byproduct_move = mo.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_byproduct
        )
        byproduct_move.quantity = 0.5
        byproduct_move._action_done()
        mo.button_mark_done()

        self.assertEqual(mo.state, "done")
        byproduct_so_line = sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertTrue(
            byproduct_so_line,
            "SO lookup via origin should have found the SO and created a line.",
        )
        self.assertAlmostEqual(byproduct_so_line.product_uom_qty, 0.5, places=2)

    def test_09_byproduct_with_zero_quantity_skipped(self):
        """A byproduct move with zero picked quantity must be skipped by
        ``_get_byproduct_moves_to_add``."""
        mo, sale_order = self._create_and_process_mo_for_sale_order(
            main_product_qty=1.0, byproduct_produced_qty=0.5
        )
        # Force the byproduct move quantity to 0 and drop its picked move
        # lines so the float_compare skip branch is exercised directly.
        byproduct_move = mo.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_byproduct
        )
        byproduct_move.move_line_ids.unlink()
        byproduct_move.quantity = 0.0

        self.assertEqual(mo._get_byproduct_moves_to_add(), [])

    def test_10_default_note_template_used(self):
        """When no custom template is set on the company, the created
        by-product line uses ``DEFAULT_BYPRODUCT_NOTE_TEMPLATE``."""
        # Make sure no custom template leaks in from another test.
        self.env.company.byproduct_note_template = False

        mo, sale_order = self._create_and_process_mo_for_sale_order(
            main_product_qty=1.0, byproduct_produced_qty=0.5
        )
        mo.button_mark_done()

        byproduct_so_line = sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertTrue(byproduct_so_line, "By-product line was not created.")

        expected_note = DEFAULT_BYPRODUCT_NOTE_TEMPLATE.replace(
            "{product_name}", self.product_byproduct.name
        ).replace("{mo_name}", mo.name)
        self.assertEqual(
            byproduct_so_line.name,
            expected_note,
            "By-product line should use the default note template.",
        )

    def test_11_fallback_quantity_without_picked_lines(self):
        """A by-product move with a positive ``quantity`` but no picked move
        lines must fall back to ``move.quantity`` in
        ``_get_byproduct_moves_to_add``."""
        mo, __ = self._create_and_process_mo_for_sale_order(
            main_product_qty=1.0, byproduct_produced_qty=0.5
        )
        byproduct_move = mo.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_byproduct
        )
        # Drop the picked move lines but keep a positive move quantity so the
        # ``else`` fallback branch (not the picked-lines sum) is taken.
        byproduct_move.move_line_ids.unlink()
        byproduct_move.quantity = 0.5

        moves_to_add = mo._get_byproduct_moves_to_add()
        self.assertEqual(len(moves_to_add), 1, "Expected one by-product move.")
        returned_move, returned_qty = moves_to_add[0]
        self.assertEqual(returned_move, byproduct_move)
        self.assertAlmostEqual(returned_qty, 0.5, places=2)

    def test_12_config_settings_note_template_write_through(self):
        """Setting the template through ``res.config.settings`` must propagate
        to the company via the related field."""
        template = "Cfg {product_name} / {mo_name}"
        settings = self.env["res.config.settings"].create(
            {"byproduct_note_template": template}
        )
        settings.execute()
        self.assertEqual(
            self.env.company.byproduct_note_template,
            template,
            "res.config.settings did not write the template through to the " "company.",
        )

    def _create_two_byproduct_bom(self):
        """Create a saleable main product whose BOM yields two distinct
        saleable by-products. Returns (main, bom, byproduct_a, byproduct_b)."""
        byproduct_a = self.product_byproduct
        byproduct_b = self.env["product.product"].create(
            {
                "name": "By-product W (second saleable)",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": self.byproduct_category.id,
                "uom_id": self.product_uom_kg.id,
                "uom_po_id": self.product_uom_kg.id,
                "route_ids": [(6, 0, [self.manufacture_route.id])],
                "standard_price": 2.0,
                "lst_price": 8.0,
                "sale_ok": True,
                "purchase_ok": False,
            }
        )
        main = self.env["product.product"].create(
            {
                "name": "Main Product Multi-BP",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": self.env.ref("product.product_category_all").id,
                "uom_id": self.product_uom_unit.id,
                "uom_po_id": self.product_uom_unit.id,
                "route_ids": [(6, 0, [self.manufacture_route.id])],
                "standard_price": 10.0,
                "lst_price": 20.0,
                "sale_ok": True,
                "purchase_ok": False,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": main.product_tmpl_id.id,
                "product_id": main.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_component.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.product_component.uom_id.id,
                        },
                    )
                ],
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": byproduct_a.id,
                            "product_qty": 0.5,
                            "product_uom_id": byproduct_a.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": byproduct_b.id,
                            "product_qty": 0.5,
                            "product_uom_id": byproduct_b.uom_id.id,
                        },
                    ),
                ],
            }
        )
        return main, bom, byproduct_a, byproduct_b

    def _process_manual_mo(self, main_product, bom, byproduct_qtys, origin):
        """Create, confirm and complete a manual MO for ``main_product`` with
        the given ``{byproduct: qty}`` yields, marking it done. ``origin`` links
        it back to a sale order by name."""
        mrp_picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id", "=", self.env.ref("stock.warehouse0").id),
            ],
            limit=1,
        )
        mo = self.env["mrp.production"].create(
            {
                "product_id": main_product.id,
                "product_qty": 1.0,
                "bom_id": bom.id,
                "product_uom_id": main_product.uom_id.id,
                "origin": origin,
                "picking_type_id": mrp_picking_type.id,
            }
        )
        mo.action_confirm()

        for move_raw in mo.move_raw_ids:
            move_raw.quantity = move_raw.product_uom_qty
            move_raw._action_done()

        main_move = mo.move_finished_ids.filtered(
            lambda m: m.product_id == main_product
        )
        main_move.quantity = main_move.product_uom_qty
        main_move._action_done()

        for byproduct, qty in byproduct_qtys.items():
            bp_move = mo.move_byproduct_ids.filtered(
                lambda m, p=byproduct: m.product_id == p
            )
            self.assertTrue(bp_move, f"By-product move for {byproduct.name} missing.")
            bp_move.quantity = qty
            bp_move._action_done()

        mo.button_mark_done()
        self.assertEqual(mo.state, "done")
        return mo

    def test_13_multiple_byproducts_batch_create(self):
        """Two distinct saleable by-products on one MO must produce two new
        flagged SO lines through the batch-create path."""
        main, bom, byproduct_a, byproduct_b = self._create_two_byproduct_bom()
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": main.id,
                            "product_uom_qty": 1.0,
                            "product_uom": main.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()

        self._process_manual_mo(
            main,
            bom,
            {byproduct_a: 0.5, byproduct_b: 0.5},
            origin=sale_order.name,
        )

        byproduct_lines = sale_order.order_line.filtered("is_mrp_byproduct_line")
        self.assertEqual(
            len(byproduct_lines), 2, "Both by-products should create SO lines."
        )
        self.assertEqual(
            byproduct_lines.mapped("product_id"),
            byproduct_a | byproduct_b,
        )

    def test_14_mixed_update_and_create(self):
        """A single MO run must update a pre-existing by-product line and create
        a new one for the other by-product in the same batch."""
        main, bom, byproduct_a, byproduct_b = self._create_two_byproduct_bom()
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": main.id,
                            "product_uom_qty": 1.0,
                            "product_uom": main.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()

        # Pre-existing flagged line for byproduct_a that must be updated.
        initial_qty = 0.2
        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": byproduct_a.id,
                "product_uom_qty": initial_qty,
                "product_uom": byproduct_a.uom_id.id,
                "is_mrp_byproduct_line": True,
            }
        )

        self._process_manual_mo(
            main,
            bom,
            {byproduct_a: 0.5, byproduct_b: 0.5},
            origin=sale_order.name,
        )

        line_a = sale_order.order_line.filtered(
            lambda li: li.product_id == byproduct_a and li.is_mrp_byproduct_line
        )
        line_b = sale_order.order_line.filtered(
            lambda li: li.product_id == byproduct_b and li.is_mrp_byproduct_line
        )
        self.assertEqual(len(line_a), 1, "Existing line should have been updated.")
        self.assertAlmostEqual(
            line_a.product_uom_qty,
            initial_qty + 0.5,
            places=2,
            msg="Existing by-product line quantity not updated.",
        )
        self.assertEqual(len(line_b), 1, "New by-product line should be created.")
        self.assertAlmostEqual(line_b.product_uom_qty, 0.5, places=2)
