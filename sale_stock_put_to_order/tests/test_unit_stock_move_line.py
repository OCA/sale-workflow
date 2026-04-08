# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestPtoCommon


class TestStockMoveLine(TestPtoCommon):
    """Tests for _apply_putaway_strategy override on stock.move.line."""

    def _enable_auto_select(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_stock_put_to_order.auto_select_location", "True"
        )

    def _create_inbound_picking(self):
        """Create a picking going INTO the PTO root with stock in supplier."""
        supplier = self.env.ref("stock.stock_location_suppliers")
        self.set_quantity(supplier, self.product, 100)
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": supplier.id,
                "location_dest_id": self.pto_root.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Auto PTO Move",
                "picking_id": picking.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "location_id": supplier.id,
                "location_dest_id": self.pto_root.id,
            }
        )
        return picking

    def test_auto_select_disabled(self):
        """Move line keeps root destination when auto-select is off."""
        picking = self._create_inbound_picking()
        picking.action_confirm()
        picking.action_assign()
        for ml in picking.move_line_ids:
            self.assertNotEqual(ml.location_dest_id, self.pto_bin_1)
            self.assertNotEqual(ml.location_dest_id, self.pto_bin_2)

    def test_auto_select_enabled(self):
        """Move line destination redirected to PTO bin when enabled."""
        self._enable_auto_select()
        picking = self._create_inbound_picking()
        picking.action_confirm()
        picking.action_assign()
        pto_bins = self.pto_bin_1 | self.pto_bin_2 | self.pto_other
        for ml in picking.move_line_ids:
            self.assertIn(ml.location_dest_id, pto_bins)

    def test_auto_select_no_pto_root(self):
        """Falls back to default when destination is not a PTO zone."""
        self._enable_auto_select()
        self.pto_root.is_pto = False
        picking = self._create_inbound_picking()
        picking.action_confirm()
        picking.action_assign()
        for ml in picking.move_line_ids:
            self.assertNotIn(
                ml.location_dest_id,
                self.pto_bin_1 | self.pto_bin_2 | self.pto_other,
            )

    def test_auto_select_no_stock(self):
        """Falls back when no PTO bin holds matching products."""
        self._enable_auto_select()
        self.reset_quantity(
            self.pto_bin_1 | self.pto_bin_2 | self.pto_other,
            self.product | self.other_product,
        )
        picking = self._create_inbound_picking()
        picking.action_confirm()
        picking.action_assign()
        pto_bins = self.pto_bin_1 | self.pto_bin_2 | self.pto_other
        for ml in picking.move_line_ids:
            self.assertNotIn(ml.location_dest_id, pto_bins)
