# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

from .common import TestPtoCommon


class TestStockPicking(TestPtoCommon):
    """Unit tests for behaviors not testable through functional tests."""

    def _first_dest(self, excluded=None):
        """Helper: return the first candidate from the generator."""
        return next(
            (
                loc
                for loc, _ in self.picking._find_pto_dest_location_and_quants(
                    excluded_locations=excluded or None
                )
            ),
            self.env["stock.location"],
        )

    def _set_write_dates(self, bin1_date, bin2_date):
        """Force write_date on quants via SQL (ORM ignores manual timestamps)."""
        for location, date in (
            (self.pto_bin_1, bin1_date),
            (self.pto_bin_2, bin2_date),
        ):
            self.env.cr.execute(
                "UPDATE stock_quant SET write_date = %s WHERE location_id = %s",
                (date, location.id),
            )
        self.env["stock.quant"].invalidate_model(["write_date"])

    # -- Write-date ordering ---------------------------------------------------

    def test_most_recent_bin_first(self):
        """First candidate is the bin with the most recently updated quants."""
        self._set_write_dates(datetime(2026, 1, 1), datetime(2026, 1, 2))
        dest = self._first_dest()
        self.assertEqual(dest, self.pto_bin_2)

    # -- Storage category ------------------------------------------------------

    def test_storage_category_rejects_bin(self):
        """Candidate rejected when storage category forbids mixed products."""
        storage_category = self.env["stock.storage.category"].create(
            {
                "name": "Limited PTO",
                "allow_new_product": "empty",
            }
        )
        self.pto_bin_2.storage_category_id = storage_category
        dest = self._first_dest(excluded=self.pto_bin_1)
        self.assertNotEqual(dest, self.pto_bin_2)

    # -- Procurement group filtering -------------------------------------------

    def _create_done_move_line(self, product, location_dest, group):
        """Create a validated move line that placed *product* in *location_dest*."""
        move = self.env["stock.move"].create(
            {
                "name": "Done PTO Move",
                "product_id": product.id,
                "product_uom_qty": 1,
                "product_uom": product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": location_dest.id,
                "group_id": group.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": location_dest.id,
                "quantity": 1,
            }
        )
        move.state = "done"

    def test_no_group_returns_all_bins(self):
        """Without procurement group all bins with stock are considered."""
        self.assertFalse(self.picking.group_id)
        locations = [
            loc for loc, _ in self.picking._find_pto_dest_location_and_quants()
        ]
        self.assertIn(self.pto_bin_1, locations)
        self.assertIn(self.pto_bin_2, locations)

    def test_group_restricts_to_matching_bins(self):
        """Only bins where the same procurement group placed products."""
        group = self.env["procurement.group"].create({"name": "SO-001"})
        self.picking.group_id = group
        self._create_done_move_line(self.product, self.pto_bin_1, group)
        locations = [
            loc for loc, _ in self.picking._find_pto_dest_location_and_quants()
        ]
        self.assertIn(self.pto_bin_1, locations)
        self.assertNotIn(self.pto_bin_2, locations)

    def test_group_no_done_moves_returns_nothing(self):
        """Group set but no done moves for that group yields nothing."""
        group = self.env["procurement.group"].create({"name": "SO-003"})
        self.picking.group_id = group
        locations = [
            loc for loc, _ in self.picking._find_pto_dest_location_and_quants()
        ]
        self.assertFalse(locations)
        locations = [
            loc for loc, _ in self.picking._find_pto_dest_location_and_quants()
        ]
        self.assertFalse(locations)
