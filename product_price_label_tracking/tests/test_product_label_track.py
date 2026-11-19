# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .common import LabelTrackingCommon


class TestProductLabelTrack(LabelTrackingCommon):
    def test_open_track_follows_new_price(self):
        track = self._scanned_track(12.0)
        self.product.list_price = 13.0
        self.rule.action_scan()
        self.assertEqual(len(self._tracks()), 2)
        self.assertRecordValues(track, [{"state": "updated", "price": 13.0}])

    def test_price_back_to_previous_cancels(self):
        track = self._scanned_track(12.0)
        self.product.list_price = 10.0
        self.rule.action_scan()
        self.assertRecordValues(track, [{"state": "cancelled", "price": 10.0}])
        self.rule.action_scan()
        self.assertEqual(len(self._tracks()), 2)

    def test_mark_printed(self):
        track = self._scanned_track(12.0)
        track.action_mark_printed()
        self.assertRecordValues(track, [{"state": "printed", "printed_price": 12.0}])

    def test_reset_to_new_clears_printed_price(self):
        track = self._scanned_track(12.0)
        track.action_mark_printed()
        track.action_reset_to_new()
        track.flush_recordset()
        self.assertRecordValues(track, [{"state": "new", "printed_price": False}])
        self.rule.action_scan()
        self.assertEqual(track.state, "new", "Same price leaves a reset track alone")

    def test_action_refused_on_wrong_status(self):
        track = self._scanned_track(12.0)
        with self.assertRaises(UserError):
            track.action_reset_to_new()
        track.action_cancel()
        with self.assertRaises(UserError):
            track.action_mark_printed()

    @mute_logger("odoo.sql_db")
    def test_one_open_track_per_rule_and_product(self):
        self._scanned_track(12.0)
        baseline = self._tracks()[1]
        with self.assertRaises(IntegrityError):
            baseline.action_reset_to_new()
            baseline.flush_recordset()

    @mute_logger("odoo.sql_db")
    def test_printed_price_only_when_printed(self):
        track = self._scanned_track(12.0)
        with self.assertRaises(IntegrityError):
            track.printed_price = 12.0
            track.flush_recordset()
