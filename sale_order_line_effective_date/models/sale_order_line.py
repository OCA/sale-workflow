# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    effective_date = fields.Datetime(
        compute="_compute_effective_dates",
        store=True,
        compute_sudo=True,
        help="Completion date of the first delivery order.",
    )
    last_effective_date = fields.Datetime(
        compute="_compute_effective_dates",
        store=True,
        compute_sudo=True,
        help="Completion date of the last delivery order.",
    )
    order_commitment_date = fields.Datetime(
        related="order_id.commitment_date",
        string="Commitment Date",
        store=True,
        readonly=True,
        help="Commitment Date set on the Order",
    )

    @api.depends("move_ids.date")
    def _compute_effective_dates(self):
        for line in self:
            moves = line.move_ids.filtered_domain(
                [
                    ("state", "=", "done"),
                    ("location_dest_id.usage", "=", "customer"),
                    ("date", "!=", False),
                ]
            ).sorted("date", reverse=False)
            line.effective_date = moves[:1].date
            line.last_effective_date = moves[-1:].date
