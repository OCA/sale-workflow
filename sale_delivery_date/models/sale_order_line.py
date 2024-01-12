# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from datetime import datetime, time, timedelta

import pytz
from pytz import UTC, timezone

from odoo import api, models

from odoo.addons.partner_tz.tools import tz_utils

_logger = logging.getLogger(__name__)

# When postponing a delivery date based on calendar leaves, it could happen
# that we have to look far in the future for a valid day.
# I.E. when customer's time window is wednesday, and all wednesdays are leaves
# on the warehouse calendar.
# In such case, it would create an infinite loop, because no matter how
# far we look in the future, we will never find an open time window for this customer.
# In order to avoid this, we use LOOP_THRESHOLD as a hard limit about how
# far in the future we are willing to look for a valid delivery date.
# If no valid delivery_date date has been found within this date range,
# then the next day (with less restrictive constraints) will be used.
LOOP_THRESHOLD = 20


class SaleOrderLine(models.Model):
    """This override adds delays to the date_deadline and the date_planned.
    As per this commit 57f805f71e9357870dfc2498c5ef72ebd8ab7273
    - On pickings, the date_deadline represents the delivery date, and the
      date_planned represents the preparation date (date_deadline - security_lead).
    - On sale orders, date_planned represents the delivery date.
    """

    _inherit = "sale.order.line"

    # =====
    # OVERRIDES
    # =====

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Add a context key, so we know in `_prepare_procurement_values` that we
        # might have to update the date based on today instead of the order date
        if previous_product_uom_qty:
            self = self.with_context(updated_line_qty=True)
        return super(SaleOrderLine, self)._action_launch_stock_rule(
            previous_product_uom_qty
        )

    def _prepare_procurement_values(self, group_id=False):
        # Here, we need to set date_deadline and date_planned correctly
        # res["date_planned"] is order.date_order + lead_time
        # So, date_planned should be:
        # date_planned - lead, on which we apply the cutoff and then the workload with
        # respect to the calendar (if any)
        # Also, date_deadline should be:
        # date_planned on which we apply the customer's time windows
        res = super()._prepare_procurement_values(group_id=group_id)
        # There's 2 cases here:
        # 1) commitment date is set, compute date_planned from date_deadline
        # 2) commitment date isn't set, update date_deadline according to
        #    cutoff / calendar / delivery window, and compute date_planned
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

    def _expected_date(self):
        # Computes the expected date with respect to the WH calendar, if any.
        # sol.expected_date is computed exactly the same way date_deadline is computed
        # in _prepare_procurement_values (date_order + customer_lead)
        date_deadline = super()._expected_date()
        delays = self._get_delays()
        cutoff = self.order_id.get_cutoff_time()
        calendar = self.order_id.warehouse_id.calendar2_id
        customer_lead, __, __ = delays
        date_order = self._deduct_delay(date_deadline, customer_lead)
        expedition_date = self._expedition_date_from_date_order(
            date_order, delays, calendar=calendar, cutoff=cutoff
        )
        partner = self.order_id.partner_shipping_id
        delivery_date = self._delivery_date_from_expedition_date(
            expedition_date, partner, calendar, delays
        )
        return delivery_date

    @api.depends("order_id.expected_date")
    def _compute_qty_at_date(self):
        """Trigger computation of qty_at_date when expected_date is updated"""
        return super()._compute_qty_at_date()

    # =====
    # Higher level methods
    # =====

    def _prepare_procurement_values_commitment_date(self, res):
        # With commitment_date set, we do not modify the date_deadline.
        # However, we can compute the date planned from it
        # 1) commitment_date - security_lead = order ready to be shipped (1)
        # 2) {1} - workload
        # 3) while {2} isn't a working day, remove 1 day
        # 4) apply cutoff (with `keep_same_day` param)
        date_planned = res["date_planned"]
        date_deadline = res["date_deadline"]
        delays = self._get_delays()
        calendar = self.order_id.warehouse_id.calendar2_id
        expedition_date = self._expedition_date_from_delivery_date(
            date_planned, date_deadline, delays, calendar=calendar
        )
        cutoff = self.order_id.get_cutoff_time()
        # TODO We should stop here, as the date_planned as defined by odoo represents
        # the expedition date (date_deadline - security_lead).
        # In a next refactor, extract the following code in a glue module
        # between stock_available_to_promise_release and this module.
        # stock_available_to_promise_release uses the date_planned as the
        # preparation date before the picking is release, and as the expedition date
        # after it has been released.
        # /TODO Put this in the roadmap
        preparation_date = self._preparation_date_from_expedition_date(
            expedition_date, delays, calendar=calendar, cutoff=cutoff
        )
        res["date_planned"] = preparation_date
        # Do not change the date_deadline
        res["date_deadline"] = date_deadline
        return res

    def _prepare_procurement_values_no_commitment_date(self, res, date_from=None):
        # See graph in docs/
        #
        # date_deadline computation:
        # 1.1) Retrieve confirmation datetime by deducing customer_lead from
        #    odoo's date_planned.
        # 1.2) Apply cutoff:
        #    - change time to cutoff if we're before cutoff
        #    - postpone to next day at cutoff otherwise
        # 1.3) Postpone to next working day if a calendar is set.
        #    Could be today, if today is a working day.
        # 1.4) Apply the workload (time it takes to process the order) with
        #    respect to calendar attendances and leaves, if set.
        # 1.5) Apply delivery delay
        # 1.6) Apply customer's delivery preference (everytime or time window)
        #
        # Since customer delivery preference might have postponed the delivery
        # by more than the delivery delay, we might have to prepare and send
        # goods later than what was computed in the previous steps 1.3) and 1.4)
        # I.E. delivery_time in previous step {1.5} is a monday, but customer
        # is configured to receive goods on fridays. Delivery date will be postponed
        # by 4 days. If we send the goods at the date computed in {1.4}, the customer
        # will receive them too early.
        # The idea here is to start from the expected_date computed in {1.6},
        # and retrieve various delays from it in order to find the latest possible
        # work_start and work_end dates.
        #
        # date_planned computation:
        # 2.1) Retrieve delivery delay from the delivery datetime, we get the
        #    optimal datetime where goods should be given to the carrier.
        # 2.2) Then, find the latest possible working attendance between
        #      the earliest_work_end computed in {1.4} (which we know is a working day)
        #      and the optimal end date computed in {2.1} (which might not be a valid date)
        # 2.3) if the latest work end computed in {2.2} is the same or earlier
        #      than the earliest_work_end, then we cannot send goods later than this
        #      and we're done
        # 2.4) Retrieve the workload from latest_work_end in order to compute
        #      the latest_work_start
        # 2.5) apply the cutoff, without changing the date if latest_work_end is
        #      after the cutoff.
        #
        # - customer_lead represents the delay between order confirmation and
        #   reception of the goods
        # - security_lead represents the delivery lead time
        # - workload represents the time needed to process the order
        #   before sending the goods.
        delays = self._get_delays()
        cutoff = self.order_id.get_cutoff_time()
        partner = self.order_id.partner_shipping_id
        calendar = self.order_id.warehouse_id.calendar2_id
        customer_lead, __, __ = delays
        if not date_from:
            date_deadline = res["date_deadline"]
            date_from = self._deduct_delay(date_deadline, customer_lead)
        earliest_expedition_date = self._expedition_date_from_date_order(
            date_from, delays, calendar=calendar, cutoff=cutoff
        )
        delivery_date = self._delivery_date_from_expedition_date(
            earliest_expedition_date, partner, calendar, delays
        )
        res["date_deadline"] = delivery_date
        expedition_date = self._expedition_date_from_delivery_date(
            earliest_expedition_date, delivery_date, delays, calendar=calendar
        )
        cutoff = self.order_id.get_cutoff_time()
        # TODO We should stop here, as the date_planned as defined by odoo represents
        # the expedition date (date_deadline - security_lead).
        # res["date_planned"] = expedition_date
        # In a next refactor, extract the following code in a glue module
        # between stock_available_to_promise_release and this module.
        # stock_available_to_promise_release uses the date_planned as the
        # preparation date before the picking is release, and as the expedition date
        # after it has been released.
        # /TODO Put this in the roadmap
        preparation_date = self._preparation_date_from_expedition_date(
            expedition_date, delays, calendar=calendar, cutoff=cutoff
        )
        res["date_planned"] = preparation_date
        return res

    @api.model
    def _expedition_date_from_date_order(
        self, date_order, delays, calendar=False, cutoff=None
    ):
        if not cutoff:
            cutoff = {}
        customer_lead, __, workload = delays
        earliest_work_start = self._apply_cutoff(date_order, cutoff)
        # Here, we added delays on an order_date without considering working days.
        # Postpone this date to a working date, if necessary.
        working_day_work_start = self._postpone_to_working_day(
            earliest_work_start, calendar=calendar
        )
        # Once we have a valid working date start, we can apply the workload, and
        # get the earliest possible work end / earliest expedition date
        earliest_expedition_date = self._add_delay(
            working_day_work_start, workload, calendar=calendar
        )
        return earliest_expedition_date

    @api.model
    def _get_naive_date_from_datetime(self, earliest_delivery_datetime, tz_string):
        """applies time.min() on a datetime with respect to customer's tz"""
        tz = timezone(tz_string)
        earliest_delivery_datetime_utc = UTC.localize(earliest_delivery_datetime)
        earliest_delivery_datetime_tz = earliest_delivery_datetime_utc.astimezone(tz)
        earliest_delivery_date_tz = datetime.combine(
            earliest_delivery_datetime_tz, time.min
        )
        return earliest_delivery_date_tz.replace(tzinfo=None)

    @api.model
    def _delivery_date_from_expedition_date(
        self, expedition_date, partner, calendar, delays
    ):
        __, security_lead, __ = delays
        # Since the delivery lead is up to the carrier, warehouse calendar is irrelevant.
        # TODO use float_compare, what is the right rounding for days?
        if security_lead > 0:
            earliest_delivery_datetime = self._add_delay(expedition_date, security_lead)
            # We might end up on a leave.
            # Just apply the calendar here in order to postpone to an open day.
            # This is kinda wrong.
            # I.E. in CH, they have different public holidays depending on
            # the state. Meaning that using the warehouse calendar for this
            # might be wrong, since customer might be in another state.
            # TODO: res.country.state.calendar ?
            open_delivery_datetime = self._postpone_to_working_day(
                datetime.combine(earliest_delivery_datetime, time.min),
                calendar=calendar,
            )
            # TODO /!\ not sure about this.
            if partner:
                tz_string = partner.tz or "UTC"
            else:
                tz_string = "UTC"
            earliest_delivery_date_naive = self._get_naive_date_from_datetime(
                open_delivery_datetime, tz_string
            )
        else:
            earliest_delivery_date_naive = expedition_date
        ignore_partner_window = self.env.context.get(
            "sale_delivery_date__ignore_customer_window"
        )
        if not partner or ignore_partner_window:
            # If no partner, do not apply delivery window
            return earliest_delivery_date_naive
        return self._get_next_open_customer_window(
            partner, calendar, from_date=earliest_delivery_date_naive
        )


    def _get_next_open_customer_window(self, partner, calendar, from_date=None):
        if from_date is None:
            from_date = datetime.today()
        # Try to find an opened customer window within LOOP_THRESHOLD
        for days in range(LOOP_THRESHOLD):
            window_date = self._apply_customer_window(
                from_date + timedelta(days=days), partner
            )
            open_date = self._postpone_to_working_day(
                datetime.combine(window_date, time.min),
                calendar=calendar,
            )
            if window_date.date() == open_date.date():
                # We found an opened delivery window
                return window_date
        # Fallback to the next customer window

        # TODO should we log something?
        window_date = self._apply_customer_window(from_date, partner)
        _logger.warning(
            f"Unable to find a valid delivery date for line {self.name}. "
            f"Falling back to {str(window_date.date())}."
        )
        return window_date

    @api.model
    def _expedition_date_from_delivery_date(
        self, earliest_expedition_date, delivery_date, delays, calendar=False
    ):
        __, security_lead, __ = delays
        # From there, we know the best delivery date, but we don't want to send
        # goods to early, or start working too early.
        # The idea is that, customer might accept deliveries on friday, but the
        # earliest_work_end might be on monday, which means that we could have
        # sent goods on Thursday instead (with delivery lead of 1 day).
        # To avoid this, from the earliest delivery date, we need to retrieve
        # the various delays applied above in order to find the latest
        # possible expedition datetime and from it, the latest preparation datetime.
        # N
        # If security_lead is 0, datetime.combine(latest_expedition_datetime, time.max)
        # would be after latest_expedition_datetime.
        # expedition_date cannot be after delivery_date
        # TODO float compare
        if security_lead > 0:
            latest_expedition_datetime = self._deduct_delay(
                delivery_date, security_lead
            )
            latest_expedition_date = datetime.combine(
                latest_expedition_datetime, time.max
            )
        else:
            latest_expedition_datetime = latest_expedition_date = delivery_date
        if latest_expedition_date < earliest_expedition_date:
            return earliest_expedition_date
        wh_expedition_date = self._get_latest_work_end_from_date_range(
            earliest_expedition_date, latest_expedition_date, calendar=calendar
        )
        if wh_expedition_date == latest_expedition_date:
            return latest_expedition_datetime
        return wh_expedition_date

    @api.model
    def _preparation_date_from_expedition_date(
        self, expedition_date, delays, calendar=None, cutoff=None
    ):
        customer_lead, security_lead, workload = delays
        if cutoff is None:
            cutoff = {}
        # But, if we found a date_end closer to the delivery_date, then we might
        # find a better work_start date.
        latest_work_start = self._deduct_delay(
            expedition_date, workload, calendar=calendar
        )
        preparation_date = self._apply_cutoff(
            latest_work_start, cutoff, keep_same_day=True
        )
        return preparation_date

    # ======
    # Generic date methods
    # ======

    @api.model
    def _add_delay(self, date_from, delay, calendar=False):
        if calendar:
            # Plan days is expecting a number of days, not a delay.
            # Adding 1 day here
            days = self._delay_to_days(delay)
            return calendar.plan_days(days, date_from, compute_leaves=True)
        return date_from + timedelta(days=delay)

    @api.model
    def _deduct_delay(self, date_from, delay, calendar=False):
        if calendar:
            days = self._delay_to_days(delay)
            return calendar.plan_days(-days, date_from, compute_leaves=True)
        return date_from - timedelta(days=delay)

    @api.model
    def _apply_cutoff(self, date_order, cutoff, keep_same_day=False):
        """Apply the cut-off time on a planned date

        The cut-off configuration is taken on the partner if set, otherwise
        on the warehouse.

        By default, if the planned date is the same day but after the cut-off,
        the new planned date is delayed one day later. The argument
        keep_same_day forces keeping the same day.
        """
        if not cutoff:
            return date_order
        return self._get_utc_cutoff_datetime(cutoff, date_order, keep_same_day)

    @api.model
    def _postpone_to_working_day(self, date_start, calendar=False):
        """Returns the nearest calendar's working day"""
        if calendar:
            # If inside an attendance, returns the nearest future working day
            # at attendance start
            return calendar.plan_hours(0, date_start, compute_leaves=True)
        return date_start

    @api.model
    def _apply_customer_window(self, delivery_date, partner):
        """Postpone a delivery date according to customer's delivery preferences"""
        if not partner or partner.delivery_time_preference == "anytime":
            return delivery_date
        return partner.next_delivery_window_start_datetime(from_date=delivery_date)

    @api.model
    def _get_latest_work_end_from_date_range(
        self, earliest_work_end, latest_expedition_date, calendar=False
    ):
        """Returns the nearest date in a calendar's attendance within a date range"""
        if calendar:
            tz_string = calendar.tz or self.env.company.partner_id.tz or "UTC"
            tz = timezone(tz_string)
            earliest_work_end_tz = earliest_work_end.astimezone(tz)
            latest_expedition_date_tz = latest_expedition_date.astimezone(tz)
            # calendar._get_closest_work_time returns a working datetime within
            # a date range. It also returns the nearest one if there's more than one.
            # If there's no working time within the date range, then it returns nothing.
            timeframe = (earliest_work_end_tz, latest_expedition_date_tz)
            latest_date_end = calendar._get_closest_work_time(
                latest_expedition_date_tz, match_end=True, search_range=timeframe
            )
            if latest_date_end:
                return latest_date_end.astimezone(UTC).replace(tzinfo=None)
            return earliest_work_end  # TODO latest_expedition_date?
        return latest_expedition_date

    @api.model
    def _delay_to_days(self, number_of_days):
        """Converts a delay to a number of days."""
        if number_of_days >= 0:
            return number_of_days + 1
        return number_of_days - 1

    def _get_delays(self):
        # customer_lead is security_lead + workload, as explained on the field
        # Those are delays and cannot be negative.
        customer_lead = max(self.customer_lead or 0.0, 0.0)
        security_lead = max(self.company_id.security_lead or 0.0, 0.0)
        workload = max(customer_lead - security_lead, 0.0)
        return customer_lead, security_lead, workload

    @api.model
    def _get_utc_cutoff_datetime(self, cutoff, date, keep_same_day=False):
        tz = cutoff.get("tz")
        if tz:
            cutoff_time = time(hour=cutoff.get("hour"), minute=cutoff.get("minute"))
            # Convert here to naive datetime in UTC
            tz_loc = pytz.timezone(tz)
            date.astimezone(tz_loc)
            tz_cutoff_datetime = datetime.combine(date.date(), cutoff_time)
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
