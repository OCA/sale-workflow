# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _expected_date(self):
        """Postpone expected_date to next preferred delivery window"""
        expected_date = super()._expected_date()
        return self._sale_partner_delivery_window_expected_date(expected_date)

    def _sale_partner_delivery_window_expected_date(self, expected_date):
        partner = self.order_id.partner_shipping_id
        if not partner or partner.delivery_time_preference == "anytime":
            return expected_date
        return partner.next_delivery_window_start_datetime(from_date=expected_date)

    def _prepare_procurement_values(self, group_id=False):
        """Consider delivery_schedule in procurement"""
        res = super()._prepare_procurement_values(group_id=group_id)
        return self._sale_partner_delivery_window_prepare_procurement_values(res)

    def _sale_partner_delivery_window_prepare_procurement_values(self, res):
        date_planned = res.get("date_planned")
        if not date_planned:
            return res
        new_date_planned = self._prepare_procurement_values_time_windows(
            fields.Datetime.to_datetime(date_planned)
        )
        if new_date_planned:
            res["date_planned"] = new_date_planned
        return res

    def _prepare_procurement_values_time_windows(self, date_planned):
        if (
            self.order_id.partner_shipping_id.delivery_time_preference != "time_windows"
            # if a commitment_date is set we don't change the result as lead
            # time and delivery windows must have been considered
            or self.order_id.commitment_date
        ):
            _logger.debug(
                "Commitment date set on order %s. Delivery window not applied "
                "on line.",
                self.order_id.name,
            )
            return
        # If no commitment date is set, we must consider next preferred delivery
        #  window to postpone date_planned

        # Remove security lead time to ensure the delivery date (and not the
        # date planned of the picking) will match delivery windows
        date_planned_without_sec_lead = date_planned + timedelta(
            days=self.order_id.company_id.security_lead
        )
        ops = self.order_id.partner_shipping_id
        next_preferred_date = ops.next_delivery_window_start_datetime(
            from_date=date_planned_without_sec_lead
        )
        # Add back security lead time
        next_preferred_date_with_sec_lead = next_preferred_date - timedelta(
            days=self.order_id.company_id.security_lead
        )
        if date_planned != next_preferred_date_with_sec_lead:
            _logger.debug(
                "Delivery window applied for order %s. Date planned for line %s"
                " rescheduled from %s to %s",
                self.order_id.name,
                self.name,
                date_planned,
                next_preferred_date_with_sec_lead,
            )
            return next_preferred_date_with_sec_lead
        else:
            _logger.debug(
                "Delivery window not applied for order %s. Date planned for line %s",
                " already in delivery window",
                self.order_id.name,
                self.name,
            )
        return

    @api.depends("order_id.expected_date")
    def _compute_qty_at_date(self):
        """Trigger computation of qty_at_date when expected_date is updated"""
        return super()._compute_qty_at_date()
