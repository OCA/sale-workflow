# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock.models import stock_move


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_priority = fields.Selection(
        stock_move.PROCUREMENT_PRIORITIES,
        help="Default priority for new sale orders of this customer. "
        "Leave empty to keep the standard priority.",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["sale_priority"]
