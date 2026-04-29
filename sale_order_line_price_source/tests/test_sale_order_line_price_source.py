from odoo.tests.common import TransactionCase


class TestSaleOrderLinePriceSource(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "type": "consu",
            }
        )
        cls.product.product_tmpl_id.list_price = 100.0

        # Create pricelist with quantity-based rule
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
            }
        )

        cls.pricelist_item_qty = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": cls.product.id,
                "compute_price": "fixed",
                "fixed_price": 90.0,
                "min_quantity": 5,
            }
        )

        cls.pricelist_item_default = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": cls.product.id,
                "compute_price": "fixed",
                "fixed_price": 95.0,
                "min_quantity": 0,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )

    def _create_sale_order(self, partner=None, pricelist=None, **kwargs):
        """Helper to create a sale order."""
        if partner is None:
            partner = self.partner
        if pricelist is None:
            pricelist = self.pricelist

        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
                **kwargs,
            }
        )

    def test_pricelist_rule_source(self):
        """
        Product with matching pricelist rule ->
        source pricelist, source item populated.
        """
        # Quantity >= 5, should match pricelist_item_qty (price 90.0)
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        self.assertEqual(
            line.price_source, "pricelist", "Should detect pricelist source"
        )
        self.assertEqual(
            line.price_source_pricelist_item_id,
            self.pricelist_item_qty,
            "Should reference the matching pricelist item",
        )
        self.assertEqual(line.price_unit, 90.0, "Price should match pricelist rule")

    def test_product_price_source_no_rule(self):
        """Product with no matching rule -> source product, source item empty."""
        # Use an empty pricelist to force fallback to product sales price.
        empty_pricelist = self.env["product.pricelist"].create(
            {
                "name": "Empty Pricelist",
            }
        )

        order = self._create_sale_order(pricelist=empty_pricelist)
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        self.assertEqual(line.price_source, "product", "Should detect product source")
        self.assertFalse(
            line.price_source_pricelist_item_id,
            "Should not reference pricelist item",
        )
        self.assertEqual(line.price_unit, 100.0, "Price should use product list price")

    def test_manual_override_source(self):
        """Manual write of price_unit -> source manual, source item empty."""
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        # Line should start with pricelist source
        self.assertEqual(line.price_source, "pricelist")

        # Manually override price_unit
        line.write({"price_unit": 85.0})

        self.assertEqual(
            line.price_source, "manual", "Should mark as manual after write"
        )
        self.assertFalse(
            line.price_source_pricelist_item_id,
            "Should clear pricelist item reference",
        )
        self.assertEqual(line.price_unit, 85.0)

    def test_price_source_follows_core_manual_price_logic(self):
        """When price_unit equals technical_price_unit, source should not be manual."""
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        # Initial state comes from pricelist.
        self.assertEqual(line.price_source, "pricelist")

        # Core logic considers this non-manual because
        # technical and functional prices match.
        line.write(
            {
                "price_unit": 88.0,
                "technical_price_unit": 88.0,
            }
        )

        self.assertEqual(
            line.price_source,
            "pricelist",
            "Matching technical and functional prices should not be marked manual.",
        )
        self.assertEqual(line.price_source_pricelist_item_id, self.pricelist_item_qty)

    def test_quantity_change_recomputes_source(self):
        """Recompute after quantity change -> provenance updates."""
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        # qty 2 matches pricelist_item_default (price 95.0)
        self.assertEqual(line.price_source, "pricelist")
        self.assertEqual(
            line.price_source_pricelist_item_id, self.pricelist_item_default
        )
        self.assertEqual(line.price_unit, 95.0)

        # Change quantity to 5, should match higher-qty rule (price 90.0)
        line.write({"product_uom_qty": 5.0})
        line._reset_price_unit()

        self.assertEqual(line.price_source, "pricelist")
        self.assertEqual(line.price_source_pricelist_item_id, self.pricelist_item_qty)
        self.assertEqual(line.price_unit, 90.0, "Price should update to qty-based rule")

    def test_manual_to_auto_reset(self):
        """Manual line can be reset back to automatic pricing."""
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        # First manual override
        line.write({"price_unit": 80.0})
        self.assertEqual(line.price_source, "manual")

        # Reset price via _reset_price_unit (simulates recalculation)
        line._reset_price_unit()

        # Should revert to pricelist source
        self.assertEqual(line.price_source, "pricelist")
        self.assertEqual(line.price_source_pricelist_item_id, self.pricelist_item_qty)
        self.assertEqual(line.price_unit, 90.0)

    def test_no_product_line_no_source(self):
        """Display lines (no product) -> source should not cause errors."""
        order = self._create_sale_order()
        # Create line without product (e.g., section line)
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "name": "Section Header",
                "display_type": "line_section",
            }
        )

        # Should not raise error; source should be product (default)
        self.assertEqual(line.price_source, "product")
        self.assertFalse(line.price_source_pricelist_item_id)

    def test_context_flag_prevents_manual_marking(self):
        """Internal auto-update writes should not mark as manual."""
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        original_source = line.price_source
        original_item = line.price_source_pricelist_item_id

        # Write with auto-update context flag should not mark as manual
        line.with_context(skip_price_source_update=True).write(
            {"price_unit": line.price_unit}
        )

        # Price source should remain unchanged
        self.assertEqual(line.price_source, original_source)
        self.assertEqual(line.price_source_pricelist_item_id, original_item)

    def test_pricelist_change_updates_source(self):
        """Changing pricelist on order should update line source."""
        # Create order with default pricelist
        order = self._create_sale_order()
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        self.assertEqual(line.price_source, "pricelist")
        first_item = line.price_source_pricelist_item_id

        # Create second pricelist with different rule
        pricelist2 = self.env["product.pricelist"].create(
            {
                "name": "Alternative Pricelist",
            }
        )

        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist2.id,
                "applied_on": "0_product_variant",
                "product_id": self.product.id,
                "compute_price": "fixed",
                "fixed_price": 85.0,
                "min_quantity": 0,
            }
        )

        # Change order pricelist (this triggers recalc in Odoo)
        order.write({"pricelist_id": pricelist2.id})
        order._recompute_prices()

        # Line should still have pricelist source but with different item
        self.assertEqual(line.price_source, "pricelist")
        self.assertNotEqual(
            line.price_source_pricelist_item_id,
            first_item,
            "Should reference new pricelist item",
        )
        self.assertEqual(line.price_source_pricelist_item_id.pricelist_id, pricelist2)
        self.assertEqual(
            line.price_unit, 85.0, "Price should update to new pricelist rule"
        )

    def test_create_line_initializes_source(self):
        """Creating a line should set initial source based on pricelist matching."""
        order = self._create_sale_order()

        # Create line - should auto-detect source
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

        # Should initialize to pricelist and the matching quantity rule.
        self.assertEqual(line.price_source, "pricelist")
        self.assertEqual(line.price_source_pricelist_item_id, self.pricelist_item_qty)

    def test_create_multi_lines_initializes_each_source(self):
        """Batch create should set provenance for each created line."""
        order = self._create_sale_order()

        lines = self.env["sale.order.line"].create(
            [
                {
                    "order_id": order.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "product_uom_id": self.product.uom_id.id,
                },
                {
                    "order_id": order.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 5.0,
                    "product_uom_id": self.product.uom_id.id,
                },
            ]
        )

        line_qty_1 = lines.filtered(lambda line: line.product_uom_qty == 1.0)
        line_qty_5 = lines.filtered(lambda line: line.product_uom_qty == 5.0)

        self.assertEqual(len(line_qty_1), 1)
        self.assertEqual(len(line_qty_5), 1)

        self.assertEqual(line_qty_1.price_source, "pricelist")
        self.assertEqual(
            line_qty_1.price_source_pricelist_item_id, self.pricelist_item_default
        )

        self.assertEqual(line_qty_5.price_source, "pricelist")
        self.assertEqual(
            line_qty_5.price_source_pricelist_item_id, self.pricelist_item_qty
        )
