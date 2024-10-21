# Copyright 2021 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    production_state = fields.Selection(
        selection=[
            ("no", "No manufacturing"),
            ("unprocessed", "Unprocessed"),
            ("partially", "Partially processed"),
            ("done", "Done"),
        ],
        string="Manufacturing state",
        compute="_compute_production_state",
        store=True,
        index=True,
    )

    @api.depends("production_ids", "production_ids.state")
    def _compute_production_state(self):
        for line in self:
            if not line.production_ids:
                line.production_state = "no"
            elif all(x.state in ["done", "cancel"] for x in line.production_ids):
                line.production_state = "done"
            elif any(x.state == "done" for x in line.production_ids):
                line.production_state = "partially"
            else:
                line.production_state = "unprocessed"
