# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MRPBoM(models.Model):
    _inherit = "mrp.bom"

    bom_line_exceptions = fields.Boolean(
        compute="_compute_bom_exceptions", string="BoM Line Exceptions"
    )
    bom_exceptions = fields.Boolean(
        compute="_compute_bom_exceptions", string="BoM Exceptions"
    )

    @api.depends("bom_line_ids.approved_bom_ok")
    def _compute_bom_exceptions(self):
        for rec in self:
            rec.bom_line_exceptions = any(
                not line.approved_bom_ok for line in rec.bom_line_ids
            )
            rec.bom_exceptions = (
                True
                if (
                    (rec.product_id and not rec.product_id.bom_ok)
                    or (rec.product_tmpl_id and not rec.product_tmpl_id.bom_ok)
                )
                else False
            )


class MRPBoMLine(models.Model):
    _inherit = "mrp.bom.line"

    approved_bom_ok = fields.Boolean(related="product_id.bom_ok", default=True)
