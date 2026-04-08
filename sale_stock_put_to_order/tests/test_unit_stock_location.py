# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestPtoCommon


class TestStockLocation(TestPtoCommon):
    """Tests for PTO flag inheritance on stock.location."""

    def test_is_pto_inheritance(self):
        """Child locations inherit PTO flag from parent."""
        self.assertTrue(self.pto_bin_1.is_pto)
        self.assertTrue(self.pto_bin_2.is_pto)
        self.assertTrue(self.pto_other.is_pto)

    def test_is_pto_clearing(self):
        """Clearing PTO on parent cascades to children."""
        self.pto_root.is_pto = False
        self.pto_bin_1.invalidate_recordset(["is_pto"])
        self.assertFalse(self.pto_bin_1.is_pto)

    def test_parent_is_pto(self):
        """parent_is_pto reflects the parent's PTO state."""
        self.assertTrue(self.pto_bin_1.parent_is_pto)
        # Root's parent is not PTO
        self.assertFalse(self.pto_root.parent_is_pto)

    def test_new_child_inherits_pto(self):
        """Newly created child inherits PTO from existing PTO parent."""
        new_child = self.env["stock.location"].create(
            {
                "name": "New PTO Child",
                "usage": "internal",
                "location_id": self.pto_root.id,
            }
        )
        self.assertTrue(new_child.is_pto)

    def test_search_pto_locations(self):
        """All child locations within the PTO root are found."""
        locations = self.pto_root._search_pto()
        self.assertIn(self.pto_bin_1, locations)
        self.assertIn(self.pto_bin_2, locations)
        self.assertIn(self.pto_other, locations)

    def test_search_pto_excluded(self):
        """Excluded locations are filtered out."""
        locations = self.pto_root._search_pto(excluded_locations=self.pto_bin_1)
        self.assertNotIn(self.pto_bin_1, locations)
        self.assertIn(self.pto_bin_2, locations)

    def test_search_pto_no_root(self):
        """Empty recordset when called on empty recordset."""
        empty = self.env["stock.location"]
        self.assertFalse(empty._search_pto())
