# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # NB: the tooltip should only display the name of the applicable exception rules,
    # not the description => don't use existing field ``exceptions_summary``
    exceptions_tooltip = fields.Char(
        compute="_compute_exceptions_tooltip",
        help="Newline-separated names of the exception rules applying to this line.",
    )

    @api.depends("exception_ids.name", "is_exception_danger")
    @api.depends_context("lang")
    def _compute_exceptions_tooltip(self):
        self.exceptions_tooltip = ""
        for sol in self.filtered("is_exception_danger"):
            sol.exceptions_tooltip = "\n".join(sol.exception_ids.mapped("name"))
