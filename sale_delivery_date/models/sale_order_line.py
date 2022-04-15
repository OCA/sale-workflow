# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, exceptions, fields, models

from odoo.addons.partner_tz.tools import tz_utils

_logger = logging.getLogger(__name__)

FIND_WORKING_DAY_COUNT = 10  # To avoid infinite loops, could be increased


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Add a context key, so we know in `_prepare_procurement_values` that we
        # might have to update the date based on today instead of the order date
        if previous_product_uom_qty:
            self = self.with_context(updated_line_qty=True)
        return super(SaleOrderLine, self)._action_launch_stock_rule(
            previous_product_uom_qty
        )

    def _prepare_procurement_values(self, group_id=False):
        # Update 'date_planned' and 'date_deadline' with respect to:
        #   - the warehouse or partner cutoff time
        #   - the warehouse calendar
        #   - the delivery time window of the customer
        # knowing that 'date_planned' is when the transfer starts to be processed
        # internally and 'date_deadline' is when the goods will be delivered to
        # the customer.
        # There's 2 cases here:
        #   1) commitment_date is set, compute date_planned from date_deadline
        #   2) commitment_date isn't set, compute date_planned and date_deadline
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.order_id.commitment_date:
            res = self._prepare_procurement_values_commitment_date(res)
        else:
            res = self._prepare_procurement_values_no_commitment_date(res)
        # If `updated_line_qty` context key is set, and now is after the computed
        # date planned, then we're late, and should postpone the delivery dates
        now = datetime.now()
        late = res["date_planned"] <= now
        if self.env.context.get("updated_line_qty") and late:
            res = self._prepare_procurement_values_no_commitment_date(res, now)
        return res

    def _prepare_procurement_values_commitment_date(self, res):
        """Set 'date_planned' according to 'commitment_date'.

        We want to find the date when we could start working on the transfers
        so we will be able to ship the goods to the customer in respect to the
        `commitment_date`.
        The 'date_deadline' is already set to the 'commitment_date' (that should
        preferably fit the partner's time window if any).
        """
        warehouse = self.order_id.warehouse_id
        partner = self.order_id.partner_id
        __, security_lead, workload = self._get_delays()
        worload_days = self._delay_to_days(workload)
        # Find the first date in the WH calendar by going back in the past, if any.
        res["date_planned"] = self._deduce_workload_and_security_lead(
            res["date_deadline"], partner, warehouse, worload_days, security_lead
        )
        return res

    def _prepare_procurement_values_no_commitment_date(self, res, date_from=None):
        """Set 'date_planned' and 'date_deadline' if no 'commitment_date'.

        If date_from is set, use it as the starting date to compute delivery dates,
        otherwise, use order's date_order.
        """
        customer_lead, security_lead, workload = self._get_delays()
        workload_days = self._delay_to_days(workload)
        if not date_from:
            date_from = self.order_id.date_order
        date_planned = (
            date_from
            + timedelta(days=customer_lead or 0.0)
            - timedelta(days=security_lead)
        )
        partner = self.order_id.partner_shipping_id
        warehouse = self.order_id.warehouse_id
        calendar = warehouse.calendar_id
        date_planned = self._apply_cutoff(date_planned, partner, warehouse)
        date_planned = self._apply_workload(date_planned, workload_days, calendar)
        date_deadline = self._apply_delivery_window(
            date_planned, partner, security_lead, calendar
        )
        date_planned = self._deduce_workload_and_security_lead(
            date_deadline, partner, warehouse, workload_days, security_lead
        )
        res.update({"date_deadline": date_deadline, "date_planned": date_planned})
        return res

    @api.model
    def _deduce_workload_and_security_lead(
        self, date_deadline, partner, warehouse, days, security_lead
    ):
        """Return the 'date_planned' from the 'date_deadline'.

        Once we know the delivery date of the customer, we are able to
        compute the final scheduled date of the transfer by taking into
        account the workload, the WH calendar and the cutoff time.
        """
        # Remove the security lead from the date_deadline
        # If there's a calendar, remove 1 day until we get to a working day.
        # The reason for that is the parcel cannot be given to the carrier
        # on a non-working day.
        calendar = warehouse.calendar_id
        date_planned = date_deadline - timedelta(days=security_lead)
        if calendar:
            next_working_day = self._next_working_day(date_planned, calendar)
            count = 0
            while next_working_day.date() != date_planned.date():
                if count > FIND_WORKING_DAY_COUNT:  # To avoid infinite loop
                    raise exceptions.UserError(
                        _(
                            "Unable to find a working day matching "
                            "customer's delivery time window."
                        )
                    )
                date_planned -= timedelta(days=1)
                next_working_day = self._next_working_day(date_planned, calendar)
                count += 1
        # Deduce the workload, if date_planned is after the cutoff
        date_planned_w_cutoff = self._apply_cutoff(
            date_planned, partner, warehouse, keep_same_day=True
        )
        if date_planned > date_planned_w_cutoff:
            date_planned = self._apply_workload(
                date_planned, -days, warehouse.calendar_id
            )
            # the correct day has already been computed, only change the cut-off time
            return self._apply_cutoff(
                date_planned, partner, warehouse, keep_same_day=True
            )
        return date_planned_w_cutoff

    @api.model
    def _apply_cutoff(self, date, partner, warehouse, keep_same_day=False):
        cutoff = self.env["sale.order"].get_cutoff_time(partner, warehouse)
        if not cutoff:
            return date
        return self._get_utc_cutoff_datetime(cutoff, date, keep_same_day)

    @api.model
    def _apply_workload(self, date, days, calendar=None):
        if calendar:
            return calendar.plan_days(days, date, compute_leaves=True)
        return date

    @api.model
    def _apply_delivery_window(
        self, date_planned, partner, security_lead, calendar=None
    ):
        date_done = date_planned + timedelta(days=security_lead)
        date_done = self._next_working_day(date_done, calendar)
        if partner.delivery_time_preference != "time_windows":
            return date_done
        next_preferred_date = partner.next_delivery_window_start_datetime(
            from_date=date_done
        )
        next_working_day = self._next_working_day(next_preferred_date, calendar)
        count = 0
        while next_working_day.date() != next_preferred_date.date():
            if count > FIND_WORKING_DAY_COUNT:  # To avoid infinite loop
                raise exceptions.UserError(
                    _(
                        "Unable to find a working day matching "
                        "customer's delivery time window."
                    )
                )
            next_preferred_date = partner.next_delivery_window_start_datetime(
                from_date=next_working_day
            )
            next_working_day = self._next_working_day(next_preferred_date, calendar)
            count += 1
        if date_done != next_preferred_date:
            # TODO : Add logs ?
            return next_preferred_date
        return next_preferred_date

    @api.model
    def _next_working_day(self, date_, calendar=None):
        """Return the next working day starting from `date_`."""
        if calendar:
            return calendar.plan_hours(0, date_, compute_leaves=True)
        return date_

    @api.model
    def _delay_to_days(self, number_of_days):
        """Converts a delay to a number of days."""
        return number_of_days + 1

    def _get_delays(self):
        # customer_lead is security_lead + workload, as explained on the field
        customer_lead = self.customer_lead or 0.0
        security_lead = self.company_id.security_lead or 0.0
        workload = customer_lead - security_lead
        return customer_lead, security_lead, workload

    def _expected_date(self):
        # Overwritten to compute the expected date with respect to:
        #   - the warehouse or partner cutoff time
        #   - the warehouse calendar
        #   - the delivery time window of the customer
        customer_lead, security_lead, workload = self._get_delays()
        date_planned = (
            (self.order_id.date_order or fields.Datetime.now())
            + timedelta(days=customer_lead or 0.0)
            - timedelta(days=security_lead)
        )
        partner = self.order_id.partner_shipping_id
        warehouse = self.order_id.warehouse_id
        calendar = warehouse.calendar_id
        workload_days = self._delay_to_days(workload)
        date_planned = self._apply_cutoff(date_planned, partner, warehouse)
        date_planned = self._apply_workload(date_planned, workload_days, calendar)
        expected_date = self._apply_delivery_window(
            date_planned, partner, security_lead, calendar
        )
        return expected_date

    @api.depends("order_id.expected_date")
    def _compute_qty_at_date(self):
        """Trigger computation of qty_at_date when expected_date is updated"""
        return super()._compute_qty_at_date()

    @api.model
    def _get_utc_cutoff_datetime(self, cutoff, date, keep_same_day=False):
        tz = cutoff.get("tz")
        if tz:
            cutoff_time = time(hour=cutoff.get("hour"), minute=cutoff.get("minute"))
            # Convert here to naive datetime in UTC
            tz_loc = pytz.timezone(tz)
            tz_date = date.astimezone(tz_loc)
            tz_cutoff_datetime = datetime.combine(tz_date, cutoff_time)
            utc_cutoff_datetime = tz_utils.tz_to_utc_naive_datetime(
                tz_loc, tz_cutoff_datetime
            )
        else:
            utc_cutoff_datetime = date.replace(
                hour=cutoff.get("hour"), minute=cutoff.get("minute"), second=0
            )
        if date <= utc_cutoff_datetime or keep_same_day:
            # Postpone delivery to today's cutoff
            new_date = utc_cutoff_datetime
        else:
            # Postpone delivery to tomorrow's cutoff
            new_date = utc_cutoff_datetime + timedelta(days=1)
        return new_date
