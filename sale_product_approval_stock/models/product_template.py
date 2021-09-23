# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ship_ok = fields.Boolean(
        string="Can be Shipped",
        compute="_compute_ship_ok_product",
        default=False,
        store=True,
    )
    candidate_ship = fields.Boolean(string="Candidate to be Shipped", default=True)

    @api.depends("candidate_ship", "product_state_id.approved_ship")
    def _compute_ship_ok_product(self):
        for product in self:
            if product.product_state_id:
                product.ship_ok = (
                    product.candidate_ship and product.product_state_id.approved_ship
                )
                if not product.ship_ok:
                    pick_ids = self.env["stock.picking"].search(
                        [
                            ("product_id", "in", product.product_variant_ids.ids),
                            (
                                "state",
                                "in",
                                ["draft", "confirmed", "waiting", "assigned"],
                            ),
                        ]
                    )
                    pick_ids._log_exception_activity_stock(product)
