# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import pytz
from datetime import datetime, time, timedelta

from odoo import _, api, exceptions, fields, models
from odoo.addons.partner_tz.tools import tz_utils


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_cutoff_time(self):
        self.ensure_one()
        partner = self.partner_shipping_id
        if (
            partner.order_delivery_cutoff_preference == "warehouse_cutoff"
            and self.warehouse_id.apply_cutoff
        ):
            return self.warehouse_id.get_cutoff_time()
        elif partner.order_delivery_cutoff_preference == "partner_cutoff":
            return self.partner_shipping_id.get_cutoff_time()
        else:
            return {}

    @api.depends(
        "partner_shipping_id.order_delivery_cutoff_preference",
        "partner_shipping_id.cutoff_time",
    )
    def _compute_expected_date(self):
        """Add dependencies to consider fixed weekdays delivery schedule"""
        return super()._compute_expected_date()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        """Postpone delivery according to cutoff time"""
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.order_id.commitment_date:
            return res
        cutoff = self.order_id.get_cutoff_time()
        if not cutoff:
            return res
        tz = cutoff.get('tz')
        date_planned = res.get("date_planned")
        if tz and tz != 'UTC':
            cutoff_time = time(hour=cutoff.get('hour'), minute=cutoff.get('minute'))
            # Convert here to naive datetime in UTC
            tz_loc = pytz.timezone(tz)
            tz_date_planned = date_planned.astimezone(tz_loc)
            tz_cutoff_datetime = datetime.combine(tz_date_planned, cutoff_time)
            utc_cutoff_datetime = tz_utils.tz_to_utc_naive_datetime(tz_loc, tz_cutoff_datetime)
        else:
            utc_cutoff_datetime = date_planned.replace(
                hour=cutoff.get('hour'), minute=cutoff.get('minute'), second=0
            )
        if date_planned <= utc_cutoff_datetime:
            # Postpone delivery for date planned before cutoff to cutoff time
            new_date_planned = date_planned.replace(
                hour=utc_cutoff_datetime.hour, minute=utc_cutoff_datetime.minute, second=0
            )
        # Postpone delivery for order confirmed after cutoff to day after
        else:
            new_date_planned = date_planned.replace(
                hour=utc_cutoff_datetime.hour, minute=utc_cutoff_datetime.minute, second=0
            ) + timedelta(days=1)
        res["date_planned"] = new_date_planned
        return res

    def _expected_date(self):
        """Postpone expected_date to next cut-off"""
        expected_date = super()._expected_date()
        cutoff = self.order_id.get_cutoff_time()
        if not cutoff:
            return expected_date
        cutoff_tz = cutoff.get('tz')
        cutoff_time = time(hour=cutoff.get('hour'), minute=cutoff.get('minute'))
        if cutoff_tz:
            utc_cutoff_time = tz_utils.tz_to_utc_time(
                cutoff_tz,
                cutoff_time,
                base_date=expected_date
            )
        else:
            utc_cutoff_time = cutoff_time
        if expected_date.time() <= utc_cutoff_time:
            return expected_date
        return expected_date + timedelta(days=1)
