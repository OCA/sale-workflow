# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from datetime import datetime, time, timedelta

import pytz

from odoo import api, models

from odoo.addons.partner_tz.tools import tz_utils

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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
        return res

    def _prepare_procurement_values_commitment_date(self, res):
        """Set 'date_planned' according to 'commitment_date'.

        We want to find the date when we could start working on the transfers
        so we will be able to ship the goods to the customer in respect to the
        `commitment_date`.
        The 'date_deadline' is already set to the 'commitment_date' (that should
        preferably fit the partner's time window if any).
        """
        # 1) compute the date when the transfer should be ready to be shipped
        date_transfer_done = res["date_deadline"] - timedelta(
            days=self.order_id.company_id.security_lead
        )
        res["date_planned"] = date_transfer_done
        # 2) Find the first date in the WH calendar (by going back in the past)
        calendar = self.order_id.warehouse_id.calendar_id
        if calendar:
            res["date_planned"] = calendar.plan_days(
                -1, res["date_planned"], compute_leaves=True
            )
        # 3) Apply the partner or warehouse cutoff if any
        res["date_planned"] = self._get_date_planned_with_cutoff_time(
            res["date_planned"]
        )
        return res

    def _prepare_procurement_values_no_commitment_date(self, res):
        """Set 'date_planned' and 'date_deadline' if no 'commitment_date'."""
        res["date_planned"] = (
            self.order_id.date_order
            + timedelta(days=self.customer_lead or 0.0)
            - timedelta(days=self.order_id.company_id.security_lead)
        )
        res["date_planned"] = self._get_date_planned_with_cutoff_time(
            res["date_planned"]
        )
        res["date_planned"] = self._get_date_planned_with_warehouse_calendar(
            res["date_planned"]
        )
        res["date_deadline"] = self._get_date_deadline_with_delivery_window(
            res["date_planned"]
        )
        res["date_planned"] = self._get_date_planned_from_date_deadline(
            res["date_deadline"]
        )
        return res

    def _get_date_planned_with_cutoff_time(self, date_planned, keep_same_day=False):
        """Apply the cut-off time on a planned date

        The cut-off configuration is taken on the partner if set, otherwise
        on the warehouse.

        By default, if the planned date is the same day but after the cut-off,
        the new planned date is delayed one day later. The argument
        keep_same_day forces keeping the same day.
        """
        cutoff = self.order_id.get_cutoff_time()
        partner = self.order_id.partner_shipping_id
        if not cutoff:
            if not self.order_id.warehouse_id.apply_cutoff:
                _logger.debug(
                    "No cutoff applied on order %s as partner %s is set to use "
                    "%s and warehouse %s doesn't apply cutoff."
                    % (
                        self.order_id,
                        partner,
                        partner.order_delivery_cutoff_preference,
                        self.order_id.warehouse_id,
                    )
                )
            else:
                _logger.warning(
                    "No cutoff applied on order %s. %s time not applied"
                    "on line %s."
                    % (self.order_id, partner.order_delivery_cutoff_preference, self)
                )
            return date_planned
        new_date_planned = self._get_utc_cutoff_datetime(
            cutoff, date_planned, keep_same_day
        )
        _logger.debug(
            "%s applied on order %s. Date planned for line %s"
            " rescheduled from %s to %s"
            % (
                partner.order_delivery_cutoff_preference,
                self.order_id,
                self,
                date_planned,
                new_date_planned,
            )
        )
        return new_date_planned

    def _get_date_planned_with_warehouse_calendar(self, date_planned):
        """Update the date planned based on the warehouse calendar if any."""
        calendar = self.order_id.warehouse_id.calendar_id
        if date_planned and calendar:
            customer_lead, security_lead, workload = self._get_delays()
            # plan_days() expect a number of days instead of a delay
            workload_days = self._delay_to_days(workload)
            # Add the workload, with respect to the wh calendar
            date_planned = calendar.plan_days(
                workload_days, date_planned, compute_leaves=True
            )
        return date_planned

    def _get_date_deadline_with_delivery_window(self, date_planned):
        """Return 'date_deadline' according to customer's time windows.

        This computation is called only if no commitment_date is set and
        if the customer's delivery time preference is "time windows".
        It will return the effective delivery date by considering the next
        preferred delivery time window of the customer.
        """
        # As the 'date_planned' is the date when the work can start on the
        # transfer, we have to add the security lead of the company to get
        # the date indicating when the transfer will be ready to be shipped.
        # From this date we will be able to compute the preferred delivery date
        # of the customer.
        date_transfer_done = date_planned + timedelta(
            days=self.order_id.company_id.security_lead
        )
        if self.order_id.partner_shipping_id.delivery_time_preference != "time_windows":
            return date_transfer_done
        ops = self.order_id.partner_shipping_id
        next_preferred_date = ops.next_delivery_window_start_datetime(
            from_date=date_transfer_done
        )
        if date_transfer_done != next_preferred_date:
            _logger.debug(
                "Delivery window applied for order %s. Date planned for line %s"
                " rescheduled from %s to %s",
                self.order_id.name,
                self.name,
                date_transfer_done,
                next_preferred_date,
            )
            return next_preferred_date
        else:
            _logger.debug(
                "Delivery window not applied for order %s. Date planned for line %s",
                " already in delivery window",
                self.order_id.name,
                self.name,
            )
        return next_preferred_date

    def _get_date_planned_from_date_deadline(self, date_deadline):
        """Return the 'date_planned' from the 'date_deadline'.

        Once we know the delivery date of the customer, we are able to
        compute the final scheduled date of the transfer by taking into
        account the workload, the WH calendar and the cutoff time.
        """
        # Remove the security lead from the date_deadline
        date_planned = date_deadline - timedelta(
            days=self.order_id.company_id.security_lead
        )
        calendar = self.order_id.warehouse_id.calendar_id
        if calendar:
            __, __, workload = self._get_delays()
            workload_days = self._delay_to_days(workload)
            date_planned = calendar.plan_days(
                -workload_days, date_planned, compute_leaves=True
            )
        return self._get_date_planned_with_cutoff_time(
            date_planned,
            # the correct day has already been computed, only change
            # the cut-off time
            keep_same_day=True,
        )

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
        # Computes the expected date with respect to:
        #   - the warehouse or partner cutoff time
        #   - the warehouse calendar
        #   - the delivery time window of the customer
        expected_date = super()._expected_date()
        expected_date = self._cutoff_time_delivery_expected_date(expected_date)
        expected_date = self._warehouse_calendar_expected_date(expected_date)
        expected_date = self._delivery_window_expected_date(expected_date)
        return expected_date

    def _warehouse_calendar_expected_date(self, expected_date):
        calendar = self.order_id.warehouse_id.calendar_id
        if calendar:
            customer_lead, security_lead, workload = self._get_delays()
            td_customer_lead = timedelta(days=customer_lead)
            td_security_lead = timedelta(days=security_lead)
            # plan_days() expect a number of days instead of a delay
            workload_days = self._delay_to_days(workload)
            # Remove customer_lead added to order_date in sale_stock
            expected_date -= td_customer_lead
            # Add the workload, with respect to the wh calendar
            expected_date = calendar.plan_days(
                workload_days, expected_date, compute_leaves=True
            )
            # add back the security lead
            expected_date += td_security_lead
        return expected_date

    def _delivery_window_expected_date(self, expected_date):
        partner = self.order_id.partner_shipping_id
        if not partner or partner.delivery_time_preference == "anytime":
            return expected_date
        return partner.next_delivery_window_start_datetime(from_date=expected_date)

    @api.depends("order_id.expected_date")
    def _compute_qty_at_date(self):
        """Trigger computation of qty_at_date when expected_date is updated"""
        return super()._compute_qty_at_date()

    def _cutoff_time_delivery_expected_date(self, expected_date):
        cutoff = self.order_id.get_cutoff_time()
        if not cutoff:
            return expected_date
        return self._get_utc_cutoff_datetime(cutoff, expected_date)

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
