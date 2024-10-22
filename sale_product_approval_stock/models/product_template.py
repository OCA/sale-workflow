# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ship_ok = fields.Boolean(
        string="Can be Shipped",
        copy=False,
        readonly=True,
    )
    candidate_ship = fields.Boolean(string="Candidate to Ship")

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new._set_ship_ok()
        return new

    def write(self, vals):
        res = super().write(vals)
        if "product_state_id" in vals or "candidate_ship" in vals:
            self._set_ship_ok()
        return res

    def _set_ship_ok(self):
        for product in self:
            if product.product_state_id:
                product.ship_ok = (
                    product.candidate_ship and product.product_state_id.approved_ship
                )
                if not product.ship_ok:
                    pick_ids = self.env["stock.picking"].search(
                        [
                            ("product_id", "=", product.id),
                            (
                                "state",
                                "in",
                                ["draft", "confirmed", "waiting", "assigned"],
                            ),
                        ]
                    )
                    pick_ids._log_exception_activity_stock(product)
