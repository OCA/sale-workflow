# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    has_customer_ref = fields.Boolean(
        compute="_compute_has_customer_ref",
        help="Technical field to display 'Customer Ref' column on moves.",
    )

    @api.depends("move_ids.customer_ref")
    def _compute_has_customer_ref(self):
        for picking in self:
            # Break on the first move having a customer ref
            picking.has_customer_ref = next(
                (
                    move
                    for move in picking.move_ids_without_package
                    if move.customer_ref
                ),
                False,
            )

    def action_detailed_operations(self):
        res = super().action_detailed_operations()
        ctx = dict(res.get("context", {}))
        ctx["has_customer_ref"] = self.has_customer_ref
        res["context"] = ctx
        return res
