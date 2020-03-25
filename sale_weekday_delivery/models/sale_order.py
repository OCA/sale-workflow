# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models

from .res_partner import WEEKDAY_MAPPING


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends(
        "order_line.customer_lead",
        "date_order",
        "order_line.state",
        "picking_policy",
        "partner_shipping_id.delivery_schedule_preference",
        "partner_shipping_id.delivery_schedule_monday",
        "partner_shipping_id.delivery_schedule_tuesday",
        "partner_shipping_id.delivery_schedule_wednesday",
        "partner_shipping_id.delivery_schedule_thursday",
        "partner_shipping_id.delivery_schedule_friday",
        "partner_shipping_id.delivery_schedule_saturday",
        "partner_shipping_id.delivery_schedule_sunday",
    )
    def _compute_expected_date(self):
        """Add dependencies to consider fixed weekdays delivery schedule"""
        return super()._compute_expected_date()

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        """Warns if commitment date is not a preferred weekday for delivery"""
        res = super()._onchange_commitment_date()
        if res:
            return res
        if (
            self.commitment_date
            and self.partner_shipping_id.delivery_schedule_preference == "fix_weekdays"
        ):
            raw_commitment_date_weekday = self.commitment_date.weekday()
            commitment_date_weekday = WEEKDAY_MAPPING.get(
                str(raw_commitment_date_weekday)
            )
            ps = self.partner_shipping_id
            if not ps.is_preferred_delivery_weekday(commitment_date_weekday):
                return {
                    "warning": {
                        "title": _(
                            "Commitment date does not match shipping "
                            "partner's Delivery schedule preference."
                        ),
                        "message": _(
                            "The delivery date is on a %s, but the shipping "
                            "partner is set to prefer deliveries on following "
                            "weekdays:\n%s"
                            % (
                                commitment_date_weekday,
                                '\n'.join(
                                    [
                                        "  * %s" % day
                                        for day
                                        in
                                        ps.get_delivery_schedule_preferred_weekdays(
                                            translate=True
                                        )
                                    ]
                                ),
                            )
                        ),
                    }
                }


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _expected_date(self):
        """Postpone expected_date to next preferred weekday"""
        expected_date = super()._expected_date()
        partner = self.order_id.partner_shipping_id
        if partner.delivery_schedule_preference == "direct":
            return expected_date
        return partner._next_delivery_schedule_preferred_date(
            expected_date
        )

    def _prepare_procurement_values(self, group_id=False):
        """Consider delivery_schedule in procurement"""
        res = super()._prepare_procurement_values(group_id=group_id)
        if (
            self.order_id.partner_shipping_id.delivery_schedule_preference != "fix_weekdays"
            # if a commitment_date is set we don't change the result as lead
            # time and delivery week days must have been considered
            or self.order_id.commitment_date
        ):
            return res
        # If no commitment date is set, we must consider next preferred delivery
        #  weekday to postpone date_planned
        date_planned = fields.Datetime.to_datetime(res.get("date_planned"))
        ops = self.order_id.partner_shipping_id
        next_preferred_date = ops._next_delivery_schedule_preferred_date(
            date_planned
        )
        if next_preferred_date != date_planned:
            res["date_planned"] = fields.Datetime.to_string(next_preferred_date)
        return res

    @api.depends(
        "product_id",
        "customer_lead",
        "product_uom_qty",
        "order_id.warehouse_id",
        "order_id.commitment_date",
        "order_id.expected_date"
    )
    def _compute_qty_at_date(self):
        """Trigger computation of qty_at_date when expected_date is updated"""
        return super()._compute_qty_at_date()
