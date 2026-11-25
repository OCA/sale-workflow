# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.tests import Form

from .common import LabelTrackingCommon


class TestProductLabelLayout(LabelTrackingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.table = cls._create_product("Table", 50.0)
        cls.rule.action_scan()
        cls.tracks = cls.Track.search(Domain("rule_id", "=", cls.rule.id))

    def _open_wizard(self, tracks):
        action = tracks.action_print_labels()
        return Form(
            self.env[action["res_model"]].with_context(**action["context"]),
            view=self.env.ref("product.product_label_layout_form"),
        )

    def test_print_marks_tracks_printed(self):
        with self._open_wizard(self.tracks) as wizard:
            table_track = self.tracks.filtered(lambda t: t.product_id == self.table)
            wizard.label_track_ids.remove(id=table_track.id)
        wizard = wizard.save()
        action = wizard.process()
        self.assertEqual(action["data"]["quantity_by_product"], {self.product.id: 1})
        self.assertEqual(
            self.tracks.mapped("state"),
            ["printed" if t.product_id == self.product else "new" for t in self.tracks],
        )

    def test_mixed_pricelists_refused(self):
        pricelist = self.env["product.pricelist"].create({"name": "Shop"})
        rule = self.Rule.create(
            {
                "name": "Shop",
                "product_domain": self.rule.product_domain,
                "pricelist_id": pricelist.id,
            }
        )
        rule.action_scan()
        with self.assertRaises(UserError):
            (self.tracks | self._tracks(rule)).action_print_labels()
