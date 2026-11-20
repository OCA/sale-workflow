# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_delay = fields.Integer(
        string="Customer Lead Time",
        help="Additional delivery lead time for this customer, in days. "
        "This delay will be added to the product's delivery lead time.",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["sale_delay"]
