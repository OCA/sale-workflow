# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import Command, fields

from .common import LabelTrackingCommon


class TestProductLabelTrackingRule(LabelTrackingCommon):
    def test_first_scan_creates_new_tracks(self):
        self.rule.action_scan()
        self.assertRecordValues(
            self._tracks(),
            [{"state": "new", "price": 10.0, "previous_price": 0.0}],
        )

    def test_price_change_creates_new_track(self):
        track = self._scanned_track(12.0)
        self.assertRecordValues(
            track,
            [
                {
                    "state": "new",
                    "previous_price": 10.0,
                    "price": 12.0,
                    "printed_price": False,
                }
            ],
        )

    def test_unchanged_price_creates_nothing(self):
        self.rule.action_scan()
        self.rule.action_scan()
        self.assertEqual(len(self._tracks()), 1)

    def test_services_and_other_products_are_ignored(self):
        service = self._create_product("Assembly", 5.0, type="service")
        other = self.env["product.product"].create({"name": "Other", "type": "consu"})
        self.rule.action_scan()
        self.assertFalse(self._tracks(product=service))
        self.assertFalse(self._tracks(product=other))

    def test_empty_rule_tracks_all_goods(self):
        rule = self.Rule.create({"name": "Everything"})
        rule.action_scan()
        self.assertTrue(self._tracks(rule))

    def test_pricelist_price(self):
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Shop",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.product.id,
                            "compute_price": "fixed",
                            "fixed_price": 8.0,
                        }
                    )
                ],
            }
        )
        rule = self.Rule.create(
            {
                "name": "Shop",
                "product_domain": self.rule.product_domain,
                "pricelist_id": pricelist.id,
            }
        )
        (self.rule | rule).action_scan()
        pricelist.item_ids.fixed_price = 7.0
        (self.rule | rule).action_scan()
        self.assertEqual(self._tracks(rule).price, 7.0)
        self.assertEqual(self._tracks().price, 10.0, "List price did not change")

    def test_location_tracks_stock_in_child_locations(self):
        stock = self.env.ref("stock.stock_location_stock")
        shelf = self.env["stock.location"].create(
            {"name": "Shelf 1", "location_id": stock.id}
        )
        unstocked = self._create_product("Lamp", 20.0, is_storable=True)
        non_storable = self._create_product("Napkins", 2.0)
        self.env["stock.quant"]._update_available_quantity(self.product, shelf, 3)
        rule = self.Rule.create(
            {
                "name": "Shop",
                "product_domain": self.rule.product_domain,
                "location_id": stock.id,
            }
        )
        rule.action_scan()
        self.assertTrue(self._tracks(rule))
        self.assertFalse(self._tracks(rule, unstocked))
        self.assertFalse(self._tracks(rule, non_storable))
        rule.include_non_storable = True
        rule.action_scan()
        self.assertTrue(self._tracks(rule, non_storable))
        self.assertFalse(self._tracks(rule, unstocked))

    def test_cron_scans_due_rules_only(self):
        self.rule.action_scan()
        not_due = self.Rule.create(
            {"name": "Weekly", "product_domain": self.rule.product_domain}
        )
        not_due.action_scan()
        not_due.interval_type = "weeks"
        self.rule.last_scan_date = fields.Datetime.now() - timedelta(days=2)
        self.product.list_price = 15.0
        cron = self.env.ref(
            "product_price_label_tracking.ir_cron_scan_label_tracking_rules"
        )
        with self.enter_registry_test_mode():
            cron.method_direct_trigger()
        self.assertEqual(self._tracks()[0].price, 15.0)
        self.assertEqual(self._tracks(not_due)[0].price, 10.0)
        self.assertGreater(self.rule.next_scan_date, fields.Datetime.now())
