# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_planner_calendar_event_id = fields.Many2one(comodel_name="calendar.event")

    def _action_confirm(self):
        event_obj = self.env["calendar.event"]
        event_type_delivery = self.env.ref("sale_planner_calendar.event_type_delivery")
        for order in self:
            if not order.expected_date or order.commitment_date:
                continue
            delivery_event = event_obj.search(
                [
                    ("target_partner_id", "=", order.partner_id.id),
                    ("start", ">", fields.Datetime.to_string(order.expected_date)),
                    ("categ_ids", "in", event_type_delivery.ids),
                ],
                order="start",
                limit=1,
            )
            if delivery_event:
                order.commitment_date = delivery_event.start
        return super()._action_confirm()

    def _prepare_calendar_event_planner(self):
        categ = self.env.ref("sale_planner_calendar.event_type_commercial_visit")
        return {
            "name": _("Sale off planning"),
            "target_partner_id": self.partner_id.id,
            "user_id": self.user_id.id,
            "start": self.date_order,
            "stop": self.date_order
            + timedelta(minutes=round((categ.duration or 1.0) * 60)),
            "off_planning": True,
            "sale_planner_state": "done",
        }

    def action_set_planner_calendar_event(self, planner_summary=False):
        orders = self.filtered(lambda so: not so.sale_planner_calendar_event_id)
        if not orders:
            return
        order_dates = orders.mapped("date_order")
        if not planner_summary:
            planner_summary = self.env["sale.planner.calendar.summary"]
        date_from = planner_summary._get_datetime_from_date_tz_hour(
            min(order_dates), self.env.company.sale_planner_order_cut_hour
        )
        date_to = planner_summary._get_datetime_from_date_tz_hour(
            max(order_dates), self.env.company.sale_planner_order_cut_hour
        ) + relativedelta(days=1)
        calendar_event_domain = [
            ("target_partner_id", "in", orders.partner_id.ids),
            ("user_id", "in", orders.user_id.ids),
            ("start", ">=", date_from),
            ("start", "<", date_to),
        ]
        if planner_summary.event_type_id:
            calendar_event_domain.append(
                ("categ_ids", "in", planner_summary.event_type_id.ids)
            )
        calendar_events = self.env["calendar.event"].search(calendar_event_domain)
        planner_summary_domain = [
            ("user_id", "in", orders.user_id.ids),
            ("date", ">=", date_from.date()),
            ("date", "<", date_to.date()),
        ]
        if planner_summary.event_type_id:
            planner_summary_domain.append(
                ("event_type_id", "=", planner_summary.event_type_id.id)
            )
        event_summaries = planner_summary or self.env[
            "sale.planner.calendar.summary"
        ].search(planner_summary_domain)
        if not event_summaries:
            return
        cut_time = date_from.time()
        for order in orders:
            event = calendar_events.filtered(
                lambda ev: ev.target_partner_id == order.partner_id
                and ev.user_id == order.user_id
                and (ev.start.combine(ev.start.date(), cut_time) <= order.date_order)
                and (
                    ev.start.combine(ev.start.date(), cut_time) + relativedelta(days=1)
                    > order.date_order
                )
            )[:1]
            if not event:
                event_summary = event_summaries.filtered(
                    lambda sm: sm.user_id == order.user_id
                    and (
                        (
                            sm.date == order.date_order.date()
                            and order.date_order.time() >= cut_time
                        )
                        or (
                            sm.date == order.date_order.date() + relativedelta(days=1)
                            and order.date_order.time() < cut_time
                        )
                    )
                )
                if len(event_summary) > 1:
                    # Sorted to select first summary without event_type
                    event_summary = event_summary.sorted("event_type_id")[:1]
                if not event_summary:
                    continue
                event_vals = order._prepare_calendar_event_planner()
                event_vals["calendar_summary_id"] = event_summary.id
                event = self.env["calendar.event"].create(event_vals)
            order.sale_planner_calendar_event_id = event

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        if self.env.context.get("calendar_summary_id"):
            planner_summary = self.env["sale.planner.calendar.summary"].browse(
                self.env.context["calendar_summary_id"]
            )
            orders.action_set_planner_calendar_event(planner_summary=planner_summary)
        return orders
