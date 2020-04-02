# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import pytz
from datetime import datetime, time, timedelta

from odoo import _, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_cutoff_time(self):
        self.ensure_one()
        partner = self.partner_shipping_id
        if partner.order_delivery_cutoff_preference == "warehouse_cutoff":
            return self.warehouse_id.get_cutoff_time()
        elif partner.order_delivery_cutoff_preference == "partner_cutoff":
            return self.partner_shipping_id.get_cutoff_time()
        else:
            raise exceptions.UserError(_("Invalid cutoff settings"))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        """Postpone delivery according to cutoff time"""
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.order_id.commitment_date:
            return res
        date_planned = res.get("date_planned")
        cutoff = self.order_id.get_cutoff_time()
        tz = cutoff.get('tz')
        if tz and tz != 'UTC':
            cutoff_time = time(hour=cutoff.get('hour'), minute=cutoff.get('minute'))
            # Convert here to naive datetime in UTC
            tz_loc = pytz.timezone(self.tz)
            utc_loc = pytz.timezone('UTC')
            tz_date_planned = date_planned.astimezone(tz_loc)
            tz_cutoff_datetime = datetime.combine(tz_date_planned, cutoff_time)
            utc_cutoff_datetime = tz_loc.localize(tz_cutoff_datetime).astimezone(utc_loc).replace(
                tzinfo=None)
        else:
            utc_cutoff_datetime = date_planned.replace(hour=cutoff.get('hour'), minute=cutoff.get('minute'))
        if date_planned <= utc_cutoff_datetime:
            # Postpone delivery for date planned before cutoff to cutoff time
            new_date_planned = date_planned.replace(
                hour=utc_cutoff_datetime.hour, minute=utc_cutoff_datetime.minute
            )
        # Postpone delivery for order confirmed after cutoff to day after
        elif date_planned > utc_cutoff_datetime:
            new_date_planned = date_planned.replace(
                hour=utc_cutoff_datetime.hour, minute=utc_cutoff_datetime.minute
            ) + timedelta(days=1)
        res["date_planned"] = new_date_planned
        return res
