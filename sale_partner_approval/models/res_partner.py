# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    sale_ok = fields.Boolean(
        compute="_compute_sale_ok_product",
        string="Can Sell To",
        default=False,
        store=True,
    )
    candidate_sale = fields.Boolean(
        string="Candidate to Sell To",
        default=True,
    )

    @api.depends("candidate_sale", "stage_id.approved_sale", "parent_id.sale_ok")
    def _compute_sale_ok_product(self):
        for partner in self:
            # Can Sell To if is candidate and current stage allows it
            # Child contacts inherit that same sale_ok value
            if partner == partner.commercial_partner_id:
                partner.sale_ok = (
                    partner.candidate_sale and partner.stage_id.approved_sale
                )
            else:
                partner.sale_ok = partner.parent_id.sale_ok
