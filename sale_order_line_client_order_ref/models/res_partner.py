# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .res_company import REF_POLICY_SELECTION


class ResPartner(models.Model):
    _inherit = "res.partner"

    so_line_client_ref_policy = fields.Selection(
        selection=REF_POLICY_SELECTION,
        string="SO Line Customer Order Ref Sync Policy",
        help=(
            "Controls how the Sales Order's Customer Order Reference is applied to "
            "sales order lines. This setting overrides the company-level "
            "configuration.\n"
            "- Always: copy the order value when it's updated.\n"
            "- Never: never sync the order value to lines."
        ),
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["so_line_client_ref_policy"]
