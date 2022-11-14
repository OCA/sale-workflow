# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPackageLevel(models.Model):
    _inherit = "stock.package_level"

    has_customer_ref = fields.Boolean(
        compute="_compute_has_customer_ref",
        help="Technical field to display 'Customer Ref' column in a package level.",
    )

    @api.depends("move_ids.customer_ref")
    def _compute_has_customer_ref(self):
        for pl in self:
            # Break on the first move or line having a customer ref
            pl.has_customer_ref = next(
                (move for move in pl.move_ids if move.customer_ref), False
            ) or next((line for line in pl.move_line_ids if line.customer_ref), False)
