# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging
from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models

from odoo.addons.partner_tz.tools import tz_utils

_logger = logging.getLogger(__name__)


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
        date_planned = res.get("date_planned")
        if not date_planned:
            return res
        new_date_planned = self._prepare_procurement_values_cutoff_time(
            fields.Datetime.to_datetime(date_planned),
            # if we have a commitment date, even if we are too late, respect
            # the original planned date (but change the time), the transfer
            # will be considered as "late"
            keep_same_day=bool(self.order_id.commitment_date),
        )
        if new_date_planned:
            res["date_planned"] = new_date_planned
        return res

    def _prepare_procurement_values_cutoff_time(
        self, date_planned, keep_same_day=False
    ):
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
            return
        tz = cutoff.get("tz")
        if tz and tz != "UTC":
            cutoff_time = time(hour=cutoff.get("hour"), minute=cutoff.get("minute"))
            # Convert here to naive datetime in UTC
            tz_loc = pytz.timezone(tz)
            tz_date_planned = date_planned.astimezone(tz_loc)
            tz_cutoff_datetime = datetime.combine(tz_date_planned, cutoff_time)
            utc_cutoff_datetime = tz_utils.tz_to_utc_naive_datetime(
                tz_loc, tz_cutoff_datetime
            )
        else:
            utc_cutoff_datetime = date_planned.replace(
                hour=cutoff.get("hour"), minute=cutoff.get("minute"), second=0
            )
        if date_planned <= utc_cutoff_datetime or keep_same_day:
            # Postpone delivery for date planned before cutoff to cutoff time
            new_date_planned = date_planned.replace(
                hour=utc_cutoff_datetime.hour,
                minute=utc_cutoff_datetime.minute,
                second=0,
            )
        # Postpone delivery for order confirmed after cutoff to day after
        else:
            new_date_planned = date_planned.replace(
                hour=utc_cutoff_datetime.hour,
                minute=utc_cutoff_datetime.minute,
                second=0,
            ) + timedelta(days=1)
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

    def _expected_date(self):
        """Postpone expected_date to next cut-off"""
        expected_date = super()._expected_date()
        cutoff = self.order_id.get_cutoff_time()
        if not cutoff:
            return expected_date
        cutoff_tz = cutoff.get("tz")
        cutoff_time = time(hour=cutoff.get("hour"), minute=cutoff.get("minute"))
        if cutoff_tz:
            utc_cutoff_time = tz_utils.tz_to_utc_time(
                cutoff_tz, cutoff_time, base_date=expected_date
            )
        else:
            utc_cutoff_time = cutoff_time
        # FIXME: consider warehouse TZ
        # See https://github.com/OCA/sale-workflow/pull/1104#discussion_r406156787
        if expected_date.time() <= utc_cutoff_time:
            return expected_date
        return expected_date + timedelta(days=1)
