# Copyright 2025 APSL Nagarro
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from pytz import timezone, utc

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(
        "Delivery Date",
        compute="_compute_commitment_date",
        store=True,
        readonly=False,
        help="This is the delivery date promised to the customer. "
        "If set, the delivery order will be "
        "scheduled based on this date rather than product lead times.",
    )

    @api.depends(
        "order_line.product_id",
        "date_order",
    )
    def _compute_commitment_date(self):
        for order in self:
            if order.commitment_date:
                continue
            order._calculate_commitment_date()

    def _calculate_commitment_date(self):
        self.ensure_one()

        max_total_lead_time = 0

        for line in self.order_line:
            product_template = line.product_id.product_tmpl_id

            current_line_lead_time = product_template.sale_delay or 0

            if product_template.attribute_extend_lead_time:
                for ptav in line.product_id.product_template_attribute_value_ids:
                    if ptav.product_attribute_value_id.lead_time:
                        current_line_lead_time += (
                            ptav.product_attribute_value_id.lead_time
                        )

            if current_line_lead_time > max_total_lead_time:
                max_total_lead_time = current_line_lead_time

        base_date_for_calculation = self.date_order

        if base_date_for_calculation:
            self.commitment_date = self._get_date_with_lead_time_from_calendar(
                base_date_for_calculation, max_total_lead_time
            )
        else:
            self.commitment_date = False

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            order._calculate_commitment_date()
        return res

    def _get_date_with_lead_time_from_calendar(self, base_datetime, lead_time_days):
        self.ensure_one()

        calendar = self.company_id.resource_calendar_id

        if not calendar:
            return base_datetime + timedelta(days=lead_time_days)

        hours_per_day = calendar.hours_per_day if calendar.hours_per_day else 8.0
        hours_to_add = lead_time_days * hours_per_day

        calendar_tz = timezone(calendar.tz) if calendar.tz else timezone("UTC")

        if not base_datetime.tzinfo:
            base_datetime_aware = utc.localize(base_datetime)
        else:
            base_datetime_aware = base_datetime

        base_dt_in_calendar_tz = base_datetime_aware.astimezone(calendar_tz)
        naive_base_dt = base_dt_in_calendar_tz.replace(tzinfo=None)

        final_datetime_aware = calendar.plan_hours(
            hours_to_add, naive_base_dt, compute_leaves=True
        )

        return final_datetime_aware.astimezone(timezone("UTC")).replace(tzinfo=None)
