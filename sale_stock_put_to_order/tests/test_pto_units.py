# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestPtoCommon


class TestPtoUnits(TestPtoCommon):
    """Unit tests for put-to-order resolution logic on stock.picking."""

    def test_get_pto_root_location(self):
        """Root location returned when destination is a PTO zone."""
        root = self.picking._get_pto_root_location()
        self.assertEqual(root, self.pto_root)

    def test_get_pto_root_location_not_pto(self):
        """Empty recordset returned when destination is not a PTO zone."""
        self.pto_root.is_pto = False
        root = self.picking._get_pto_root_location()
        self.assertFalse(root)

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

    def test_find_pto_dest_location_with_stock(self):
        """Destination found where product already has positive stock."""
        dest = self._first_dest(excluded=self.pto_bin_1)
        self.assertEqual(dest, self.pto_bin_2)

    def test_find_pto_dest_location_deterministic_order(self):
        """First candidate is the bin with the lowest ID."""
        dest = self._first_dest()
        self.assertEqual(dest, self.pto_bin_1)

    def test_find_pto_dest_location_no_stock(self):
        """Empty recordset when no location holds matching products."""
        self.reset_quantity(
            self.pto_bin_1 | self.pto_bin_2 | self.pto_other,
            self.product | self.other_product,
        )
        dest = self._first_dest(excluded=self.pto_bin_1)
        self.assertFalse(dest)

    def test_find_pto_dest_location_storage_category(self):
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

    def test_get_pto_source_products_from_moves(self):
        """Products sourced from picking moves."""
        products = self.picking._get_pto_source_products()
        self.assertEqual(products, self.product)

    def test_get_pto_bin_groups(self):
        """Bin groups returned per-product for valid candidate locations."""
        bin_groups = self.picking._get_pto_bin_groups()
        self.assertIn(self.product.id, bin_groups)
        self.assertEqual(bin_groups[self.product.id]["name"], self.pto_bin_1.name)

    def test_is_pto_location_valid(self):
        """Valid candidate with positive stock passes validation."""
        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.pto_bin_1.id),
                ("product_id", "=", self.product.id),
            ]
        )
        self.assertTrue(
            self.picking._is_pto_location_valid(self.pto_bin_1, quants),
        )
