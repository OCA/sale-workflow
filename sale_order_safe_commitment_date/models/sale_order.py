# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(
        compute="_compute_commitment_date",
        store=True,
        readonly=False,
    )
    is_commitment_date_unsafe = fields.Boolean(
        compute="_compute_is_commitment_date_unsafe",
    )

    @api.depends("expected_date")
    def _compute_commitment_date(self):
        for sale in self.filtered(
            lambda x: x.expected_date and x.state in ["draft", "sent"]
        ):
            sale.commitment_date = sale.expected_date

    @api.depends("commitment_date", "expected_date", "state")
    def _compute_is_commitment_date_unsafe(self):
        """A commitment date is considered unsafe if it is before the expected date as
        the products won't be delivered on time."""
        self.is_commitment_date_unsafe = False
        self.filtered(
            lambda x: x.commitment_date
            and x.expected_date
            and x.state in {"draft", "sent"}
            and x.commitment_date < x.expected_date
        ).is_commitment_date_unsafe = True

    def action_confirm(self):
        # Ensure that the deliveries get on time
        unsafe_commitment_orders = self.filtered("is_commitment_date_unsafe")
        for order in unsafe_commitment_orders:
            order.commitment_date = order.expected_date
        return super().action_confirm()
