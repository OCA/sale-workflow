# Copyright 2021 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    @api.depends("order_line.production_state")
    def _compute_production_state(self):
        for order in self:
            production_states = [x.production_state for x in order.order_line]
            if all(x == "no" for x in production_states):
                order.production_state = "no"
            elif all(x in ["done", "no"] for x in production_states):
                order.production_state = "done"
            elif all(x in ["unprocessed", "no"] for x in production_states):
                order.production_state = "unprocessed"
            else:
                order.production_state = "partially"
