# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    periodicity = fields.Integer(
        string="Run every (in seconds)",
        help="Sets a periodicity for this workflow to be executed (in seconds)",
    )
    next_execution = fields.Datetime(readonly=True)
    periodicity_check_create_date = fields.Boolean(
        string="Enforce on creation time",
        help="When checked only sales created before the last execution will"
        " be processed.",
    )

    def write(self, vals):
        if "periodicity" in vals.keys():
            periodicity = vals["periodicity"]
            if periodicity == 0:
                vals["next_execution"] = False
            else:
                now = fields.Datetime.now()
                vals["next_execution"] = fields.Datetime.add(now, seconds=periodicity)
        return super().write(vals)
