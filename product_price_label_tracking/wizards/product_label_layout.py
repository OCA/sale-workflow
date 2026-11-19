# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = "product.label.layout"

    label_track_ids = fields.Many2many("product.label.track", string="Label Tracks")

    def process(self):
        self.ensure_one()
        if self.label_track_ids:
            self.write(
                {
                    "product_ids": self.label_track_ids.product_id,
                    "product_tmpl_ids": False,
                    "pricelist_id": self.label_track_ids.pricelist_id,
                }
            )
        action = super().process()
        self.label_track_ids.action_mark_printed()
        return action
