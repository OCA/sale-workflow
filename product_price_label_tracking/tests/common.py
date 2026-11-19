# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Domain

from odoo.addons.base.tests.common import BaseCommon


class LabelTrackingCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rule = cls.env["product.label.tracking.rule"]
        cls.Track = cls.env["product.label.track"]
        cls.categ = cls.env["product.category"].create({"name": "Shelf"})
        cls.product = cls._create_product("Chair", 10.0, is_storable=True)
        cls.rule = cls.Rule.create(
            {
                "name": "All shelf goods",
                "product_domain": f"[('categ_id', '=', {cls.categ.id})]",
            }
        )

    @classmethod
    def _create_product(cls, name, price, **vals):
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "list_price": price,
                "categ_id": cls.categ.id,
                **vals,
            }
        )

    def _tracks(self, rule=None, product=None):
        return self.Track.search(
            Domain("rule_id", "=", (rule or self.rule).id)
            & Domain("product_id", "=", (product or self.product).id)
        )

    def _scanned_track(self, price, rule=None):
        """Scan and print, change the price, scan again: return the new track."""
        rule = rule or self.rule
        rule.action_scan()
        self._tracks(rule).action_mark_printed()
        self.product.list_price = price
        rule.action_scan()
        return self._tracks(rule)[0]
