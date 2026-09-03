# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from datetime import datetime, time, timedelta

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
    expected_day = fields.Date(
        compute="_compute_expected_day",
        help="Based on lead time and order allowance",
    )
    delivery_day = fields.Date(
        compute="_compute_delivery_day",
    )
    is_commitment_date_unsafe = fields.Boolean(
        compute="_compute_is_commitment_date_unsafe"
    )
    in_sale_cutoff_hour = fields.Boolean(compute="_compute_in_sale_cutoff_hour")

    @api.depends("commitment_date")
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
                # Compose a datetime at 00:00 in user's local time
                local_dt = tz.localize(
                    datetime.combine(order.date_for_commitment, time(0, 0, 0))
                )
                dt_utc = local_dt.astimezone(pytz.utc)
                # Store as naive UTC datetime in Odoo
                order.commitment_date = dt_utc.replace(tzinfo=None)
            else:
                order.commitment_date = False

    @api.depends("order_line.customer_lead", "date_order", "state")
    def _compute_expected_day(self):
        """Get the next day based on lead times. I.e.: 0 -> today, 1 -> tomorrow, and so
        on. When we're in the order cut-off window, a day will be added, so:
        0 -> tomorrow, 1 -> the day after tomorrow.
        """
        # We can't just declare the field as related, as the tz computation wouldn't
        # be correct.
        # Prefetch indication
        self.mapped("order_line")
        for order in self:
            if order.state == "cancel":
                order.expected_day = False
                continue
            dates_list = order.order_line.filtered(
                lambda line: not line.display_type and not line._is_delivery()
            ).mapped(lambda line: line and line._expected_day())
            if dates_list:
                # We can use `_select_expected_date` as it returns min or max dates
                order.expected_day = order._select_expected_date(dates_list)
            else:
                order.expected_day = False

    @api.depends("date_for_commitment", "order_line")
    def _compute_delivery_day(self):
        self.delivery_day = False
        for order in self.filtered(lambda x: x.state in {"draft", "sent"}):
            if order.date_for_commitment:
                order.delivery_day = order.date_for_commitment
                continue
            dates_list = order.order_line.filtered(
                lambda line: not line.display_type and not line._is_delivery()
            ).mapped(
                lambda line: line
                and line.with_context(ignore_cutoff_hour=True)._expected_day()
            )
            if dates_list:
                # We can use `_select_expected_date` as it returns min or max dates
                order.delivery_day = order._select_expected_date(dates_list)

    @api.depends("company_id")
    def _compute_in_sale_cutoff_hour(self):
        self.in_sale_cutoff_hour = False
        for company, orders in (
            self.filtered(lambda x: x.state in {"draft", "sent"})
            .grouped("company_id")
            .items()
        ):
            orders.in_sale_cutoff_hour = company.in_sale_cutoff_hour

    @api.onchange("date_for_commitment")
    def _onchange_date_for_commitment(self):
        """React on the UI"""
        self._inverse_date_for_commitment()

    @api.onchange("commitment_date", "expected_date")
    def _onchange_commitment_date(self):
        # Just consider the whole days
        if (
            self.date_for_commitment
            and self.expected_day
            and self.date_for_commitment < self.expected_day
        ):
            return super()._onchange_commitment_date()

    @api.depends(
        "date_for_commitment",
        "delivery_day",
        "order_line.customer_lead",
        "order_line",
        "state",
    )
    def _compute_is_commitment_date_unsafe(self):
        """A commitment date is considered unsafe if it is before the expected day as
        the products won't be delivered on time."""
        self.is_commitment_date_unsafe = False
        self.filtered(
            lambda x: x.expected_day
            and x.state in {"draft", "sent"}
            and (x.date_for_commitment or x.delivery_day)
            and (x.date_for_commitment or x.delivery_day) < x.expected_day
        ).is_commitment_date_unsafe = True

    def action_confirm(self):
        # Ensure that the deliveries get on time
        unsafe_commitment_orders = self.filtered("is_commitment_date_unsafe")
        for order in unsafe_commitment_orders:
            order.date_for_commitment = order.expected_day
            order._inverse_date_for_commitment()
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _expected_day(self) -> datetime.date:
        """Similar to `_expected_date` but we return a `datetime.date`"""
        self.ensure_one()
        tz = pytz.timezone(self.env.user.tz or "UTC")
        if self.state == "sale" and self.order_id.date_order:
            order_date_utc = self.order_id.date_order.replace(tzinfo=pytz.utc)
            expected_date = order_date_utc.astimezone(tz).date()
        else:
            expected_date = fields.Date.today()
        customer_lead = self.customer_lead
        # Consider here the cut-off window
        if self.order_id.company_id.in_sale_cutoff_hour and not self.env.context.get(
            "ignore_cutoff_hour"
        ):
            customer_lead += 1
        expected_date = expected_date + timedelta(days=customer_lead)
        extra_days_to_deliver = self.order_id.company_id._days_to_deliver(expected_date)
        if extra_days_to_deliver:
            expected_date = expected_date + timedelta(days=extra_days_to_deliver)
        return expected_date
