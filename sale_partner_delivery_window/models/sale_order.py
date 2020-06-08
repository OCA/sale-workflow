# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.tools.misc import format_datetime

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends(
        "partner_shipping_id.delivery_time_preference",
        "partner_shipping_id.delivery_time_window_ids",
        "partner_shipping_id.delivery_time_window_ids.time_window_start",
        "partner_shipping_id.delivery_time_window_ids.time_window_end",
        "partner_shipping_id.delivery_time_window_ids.time_window_weekday_ids",
    )
    def _compute_expected_date(self):
        """Add dependencies to consider fixed delivery windows"""
        return super()._compute_expected_date()

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        """Warns if commitment date is not a preferred window for delivery"""
        res = super()._onchange_commitment_date()
        if res:
            return res
        if (
            self.commitment_date
            and self.partner_shipping_id.delivery_time_preference == "time_windows"
        ):
            ps = self.partner_shipping_id
            if not ps.is_in_delivery_window(self.commitment_date):
                return {
                    "warning": {
                        "title": _(
                            "Commitment date does not match shipping "
                            "partner's Delivery time schedule preference."
                        ),
                        "message": _(
                            "The delivery date is %s, but the shipping "
                            "partner is set to prefer deliveries on following "
                            "time windows:\n%s"
                            % (
                                format_datetime(self.env, self.commitment_date),
                                "\n".join(
                                    [
                                        "  * %s" % w.display_name
                                        for w in ps.get_delivery_windows().get(ps.id)
                                    ]
                                ),
                            )
                        ),
                    }
                }


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _expected_date(self):
        """Postpone expected_date to next preferred delivery window"""
        expected_date = super()._expected_date()
        partner = self.order_id.partner_shipping_id
        if not partner or partner.delivery_time_preference == "anytime":
            return expected_date
        return partner.next_delivery_window_start_datetime(from_date=expected_date)

    def _prepare_procurement_values(self, group_id=False):
        """Consider delivery_schedule in procurement"""
        res = super()._prepare_procurement_values(group_id=group_id)
        if (
            self.order_id.partner_shipping_id.delivery_time_preference != "time_windows"
            # if a commitment_date is set we don't change the result as lead
            # time and delivery windows must have been considered
            or self.order_id.commitment_date
        ):
            _logger.debug(
                "Commitment date set on order %s. Delivery window not applied "
                "on line." % self.order_id
            )
            return res
        # If no commitment date is set, we must consider next preferred delivery
        #  window to postpone date_planned
        date_planned = fields.Datetime.to_datetime(res.get("date_planned"))
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
                " rescheduled from %s to %s"
                % (self.order_id, self, date_planned, next_preferred_date_with_sec_lead)
            )
            res["date_planned"] = next_preferred_date_with_sec_lead
        else:
            _logger.debug(
                "Delivery window not applied for order %s. Date planned for line %s"
                " already in delivery window" % (self.order_id, self)
            )
        return res

    @api.depends("order_id.expected_date")
    def _compute_qty_at_date(self):
        """Trigger computation of qty_at_date when expected_date is updated"""
        return super()._compute_qty_at_date()
