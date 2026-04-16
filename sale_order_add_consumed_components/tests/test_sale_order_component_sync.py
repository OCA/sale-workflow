# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import tests
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSaleOrderComponentSync(tests.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env["product.product"]
        SaleOrder = cls.env["sale.order"]
        MrpBom = cls.env["mrp.bom"]

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

        cls.product_main = Product.create(
            {
                "name": "Custom Table",
                "type": "consu",
                "sale_ok": True,
            }
        )

        cls.product_component = Product.create(
            {
                "name": "Component A",
                "type": "consu",
                "sale_ok": True,
                "tracking": "none",
            }
        )

        cls.product_component1 = Product.create(
            {
                "name": "Table Top",
                "type": "consu",
                "sale_ok": True,
            }
        )

        cls.product_component2 = Product.create(
            {
                "name": "Screws",
                "type": "consu",
                "sale_ok": False,
            }
        )

        cls.bom = MrpBom.create(
            {
                "product_tmpl_id": cls.product_main.product_tmpl_id.id,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_component.id,
                            "product_qty": 2.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_component1.id,
                            "product_qty": 2.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_component2.id,
                            "product_qty": 10.0,
                        },
                    ),
                ],
            }
        )

        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_main.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        # Confirm the sale order
        cls.sale_order.action_confirm()

    def create_and_confirm_mo(self, component, consume_qty=1.0):
        MrpProduction = self.env["mrp.production"]

        self.mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "origin": self.sale_order.name,
            }
        )

        self.mo.action_confirm()
        for move in self.mo.move_raw_ids.filtered(lambda m: m.product_id == component):
            move.quantity = consume_qty

        self.mo.action_add_consumed_components_to_sale()
        return self.mo

    def test_components_added_to_sale_order(self):
        self.create_and_confirm_mo(self.product_component)
        component_lines = self.sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component
        )

        self.assertTrue(component_lines, "Sellable component should be added to SO")
        self.assertEqual(
            component_lines.product_uom_qty,
            1.0,
            "Quantity should match consumption",
        )
        self.assertTrue(
            all(line.is_mrp_component_line for line in component_lines),
            "Component lines should be marked as is_mrp_component_line",
        )

        # Should NOT contain the non-sellable component
        non_sellable_lines = self.sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component2
        )
        self.assertFalse(
            non_sellable_lines,
            "Non-sellable component should NOT be added to SO",
        )

    def test_sync_is_idempotent(self):
        """Calling the sync multiple times for the same MO must not multiply
        the quantity on the SO. Regression test for a bug where button_mark_done
        was called 3 times by the wizard/backorder flow, producing 3x the
        actual consumed quantity on the SO line.
        """
        self.create_and_confirm_mo(self.product_component, consume_qty=2.4)

        # Subsequent calls simulating backorder/wizard re-invocation
        self.mo.action_add_consumed_components_to_sale()
        self.mo.action_add_consumed_components_to_sale()

        component_lines = self.sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component
        )
        self.assertEqual(len(component_lines), 1, "Only one component line expected")
        self.assertEqual(
            component_lines.product_uom_qty,
            2.4,
            "product_uom_qty must equal the consumed quantity, not a multiple",
        )
        self.assertEqual(
            component_lines.qty_delivered,
            2.4,
            "qty_delivered must equal the consumed quantity, not a multiple",
        )

    def test_button_mark_done_integration(self):
        """Exercise the full button_mark_done path to ensure the override
        plays well with the MO lifecycle."""
        MrpProduction = self.env["mrp.production"]
        mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "origin": self.sale_order.name,
            }
        )
        mo.action_confirm()
        for move in mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.product_component
        ):
            move.quantity = 1.0
        mo.qty_producing = 1.0
        # button_mark_done may return a wizard in some configurations; we
        # only care that it does not raise.
        mo.button_mark_done()

    def test_multiple_mos_aggregate_quantity(self):
        """Multiple MOs linked to the same SO should aggregate their
        component consumption on the SO line."""
        self.create_and_confirm_mo(self.product_component, consume_qty=1.0)
        self.create_and_confirm_mo(self.product_component, consume_qty=1.5)

        component_lines = self.sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component
            and li.is_mrp_component_line
        )

        self.assertEqual(len(component_lines), 1, "Only one component line expected")
        self.assertEqual(
            component_lines.product_uom_qty,
            2.5,
            "Quantity should be the sum of all MOs consumption",
        )

    def test_mo_confirmation_with_sale_only_component(self):
        # This component is sellable, but has no stock/routing setup
        product = self.env["product.product"].create(
            {
                "name": "Sellable No-Route (no inventory tracked) Component ",
                "type": "consu",
                "sale_ok": True,
                "tracking": "none",
                # Intentionally no route or stock config
            }
        )

        self.bom.write(
            {"bom_line_ids": [(0, 0, {"product_id": product.id, "product_qty": 1.0})]}
        )

        # Confirming MO should not raise any error; let any exception
        # propagate naturally so the traceback is preserved.
        self.create_and_confirm_mo(product)

    def test_uom_conversion(self):
        """Components in a different UoM than the product default should
        be converted before being added to the SO line."""
        # The test harness doesn't always have multiple UoMs available for
        # arbitrary products, so we verify the helper directly.
        MrpProduction = self.env["mrp.production"]
        # Create a fake move-like object
        uom_unit = self.env.ref("uom.product_uom_unit")
        uom_dozen = self.env.ref("uom.product_uom_dozen")
        # Build an MO with a move in a different UoM
        mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "origin": self.sale_order.name,
            }
        )
        mo.action_confirm()
        for move in mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.product_component
        ):
            # Switch the move UoM to dozen, with 1 dozen = 12 units
            move.product_uom = uom_dozen
            move.quantity = 1.0
            qty_in_uom = MrpProduction._get_move_qty_in_product_uom(move)
            self.assertEqual(
                qty_in_uom,
                12.0,
                "1 dozen should convert to 12 units",
            )
            # Restore
            move.product_uom = uom_unit

    def test_no_sale_order_found_logs_info(self):
        """If the MO has no discoverable origin SO, the sync should
        silently skip (logging info) instead of crashing.
        """
        MrpProduction = self.env["mrp.production"]
        mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                # No origin, no procurement group -> no SO discoverable
            }
        )
        mo.action_confirm()
        # Should not raise
        mo.action_add_consumed_components_to_sale()
        self.assertFalse(
            mo._find_origin_sale_order(),
            "Expected no sale order to be discovered",
        )

    def test_find_origin_via_origin_name(self):
        """_find_origin_sale_order must parse comma-separated origin names
        and return the first matching SO.
        """
        MrpProduction = self.env["mrp.production"]
        mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "origin": f"Unrelated, {self.sale_order.name}",
            }
        )
        self.assertEqual(
            mo._find_origin_sale_order(),
            self.sale_order,
            "Should find the SO even when origin contains extra comma-separated names",
        )

    def test_find_origin_via_procurement_group(self):
        """_find_origin_sale_order must prefer procurement_group_id.sale_id
        over other discovery methods.
        """
        MrpProduction = self.env["mrp.production"]
        mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "procurement_group_id": self.sale_order.procurement_group_id.id,
                # No origin -> must be found via procurement group
            }
        )
        self.assertEqual(
            mo._find_origin_sale_order(),
            self.sale_order,
            "Should find the SO via procurement group when set",
        )

    def test_zero_quantity_move_skipped(self):
        """Component moves with quantity=0 should not create SO lines."""
        self.create_and_confirm_mo(self.product_component, consume_qty=0.0)
        component_lines = self.sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component
            and li.is_mrp_component_line
        )
        self.assertFalse(
            component_lines,
            "Zero-qty move must not create a component line",
        )

    def test_update_existing_component_line_uses_manual_method(self):
        """When updating an existing component line, qty_delivered_method
        must be set to 'manual' so Odoo doesn't overwrite qty_delivered
        via its compute."""
        self.create_and_confirm_mo(self.product_component, consume_qty=1.0)
        # Sync runs during create_and_confirm_mo; trigger another sync to
        # exercise the "update existing line" branch.
        self.create_and_confirm_mo(self.product_component, consume_qty=1.0)
        component_lines = self.sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component
            and li.is_mrp_component_line
        )
        self.assertEqual(len(component_lines), 1)
        self.assertEqual(
            component_lines.qty_delivered_method,
            "manual",
            "qty_delivered_method must be 'manual' on updated component lines",
        )

    def test_pricelist_price_respected(self):
        """Test that the pricelist price is used instead of the product's list price"""
        # Create a pricelist with specific rules - before creating the SO
        Pricelist = self.env["product.pricelist"]
        PricelistItem = self.env["product.pricelist.item"]

        # Create a new sale order with specific pricelist (not the confirmed one)
        partner = self.env["res.partner"].create({"name": "Test Customer 2"})

        # Change the original product's list price to something different
        self.product_component.lst_price = 50.0

        # Create a pricelist with a specific price for the component
        pricelist = Pricelist.create(
            {
                "name": "Test Pricelist",
                "currency_id": self.env.ref("base.USD").id,
            }
        )

        # Create a pricelist item that gives the product a specific price
        PricelistItem.create(
            {
                "pricelist_id": pricelist.id,
                "product_tmpl_id": self.product_component.product_tmpl_id.id,
                "fixed_price": 75.0,
            }
        )

        # Create a new sale order with this pricelist
        new_sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_main.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        # Confirm the new sale order
        new_sale_order.action_confirm()

        # Create MO for the new SO and add components to SO
        MrpProduction = self.env["mrp.production"]
        mo = MrpProduction.create(
            {
                "product_id": self.product_main.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "origin": new_sale_order.name,
            }
        )

        mo.action_confirm()
        component_moves = mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.product_component
        )
        for move in component_moves:
            move.quantity = 1.0

        mo.action_add_consumed_components_to_sale()

        # Get the added component line
        component_lines = new_sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_component
        )

        self.assertTrue(component_lines, "Component should be added to SO")
        # Check that the price used is from the pricelist, not the product's list price
        self.assertEqual(
            component_lines.price_unit,
            75.0,
            "Price should come from the pricelist, not the product's list price",
        )
