# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def is_using_quotation_number(self, vals):
        # sale_quotation_number assigns the quotation sequence number to every new
        # order when the company is not keeping a single enumeration. That overrides
        # orders belonging to a team that has its own dedicated sequence
        # (sale_team_sale_sequence).
        #
        # A team with a dedicated sequence has it's own numbering,
        # so opt those orders out of the quotation number.
        team_id = vals.get("team_id")
        if team_id and self.env["crm.team"].browse(team_id).sequence_id:
            return False
        return super().is_using_quotation_number(vals)
