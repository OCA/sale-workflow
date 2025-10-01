# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from datetime import datetime, time

import pytz

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    date_for_commitment = fields.Date(
        string="Delivery date",
        compute="_compute_date_for_commitment",
        inverse="_inverse_date_for_commitment",
        readonly=False,
        help="This is the delivery date promised to the customer. "
        "If set, the delivery order will be scheduled based on "
        "this date rather than product lead times.",
    )
    is_commitment_date_unsafe = fields.Boolean(
        compute="_compute_is_commitment_date_unsafe", store=True
    )

    # We need to avoid this trigger as the UI will do a circular change when we try
    # to set the hour manually -> it would trigger the compute -> and the compute would
    # trigger the onchange. Maybe this could be solved more properly adding a compute
    # to commitment_date, but currently the side effect is minimal so we keep it simple.
    # @api.depends("commitment_date")
    def _compute_date_for_commitment(self):
        """By default we simply get the commitment date attending to the proper tz"""
        tz = pytz.timezone(self.env.user.tz or "UTC")
        self.date_for_commitment = False
        for order in self.filtered("commitment_date"):
            commitment_utc = order.commitment_date.replace(tzinfo=pytz.utc)
            order.date_for_commitment = commitment_utc.astimezone(tz).date()

    def _inverse_date_for_commitment(self):
        """Always set the last possible minute of that date so users don't have to
        worry about non integer lead times"""
        tz = pytz.timezone(self.env.user.tz or "UTC")
        for order in self:
            if order.date_for_commitment:
                # Compose a datetime at 23:59:59 in user's local time
                local_dt = tz.localize(
                    datetime.combine(order.date_for_commitment, time(23, 59, 59))
                )
                dt_utc = local_dt.astimezone(pytz.utc)
                # Store as naive UTC datetime in Odoo
                order.commitment_date = dt_utc.replace(tzinfo=None)
            else:
                order.commitment_date = False

    @api.onchange("date_for_commitment")
    def _onchange_date_for_commitment(self):
        """React on the UI"""
        self._inverse_date_for_commitment()

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
