# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    sale_ok = fields.Boolean(
        string="Can Sell To",
        copy=False,
        readonly=True,
    )
    candidate_sale = fields.Boolean(string="Candidate to Sell To")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "candidate_sale" in fields and "candidate_sale" not in res:
            # Set default when creating from Sale App menu
            res["candidate_sale"] = bool(res.get("customer_rank"))
        return res

    def _set_sale_ok(self):
        # Candidate Sale is set/changed only in draft state
        # Can Sale is set only when not in draft state
        # This allows for Candidate Sale changes to be effective only after approval
        for partner in self.filtered(lambda x: x.stage_id.state != "draft"):
            if partner.parent_id:
                # Child contacts inherit that same sale_ok value
                ok = partner.parent_id.sale_ok
            else:
                ok = partner.candidate_sale and partner.stage_id.approved_sale
            super(Partner, partner).write({"sale_ok": ok})

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new._set_sale_ok()
        return new

    def write(self, vals):
        res = super().write(vals)
        # Do not set ok flag when moving to draft state
        if "stage_id" in vals:
            to_state = self.env["res.partner.stage"].browse(vals["stage_id"]).state
            to_state != "draft" and self._set_sale_ok()
        return res
