# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.tools import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_planner_calendar_event_id = fields.Many2one(
        comodel_name="sale.planner.calendar.event"
    )

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
                order.commitment_date = delivery_event.start_datetime
        return super()._action_confirm()

    def _prepare_calendar_event_planner(self):
        return {
            "name": _("Sale off planning"),
            "partner_id": self.partner_id.id,
            "user_id": self.user_id.id,
            "date": self.date_order,
            "off_planning": True,
            "state": "done",
        }

    def action_set_planner_calendar_event(self):
        orders = self.filtered(lambda so: not so.sale_planner_calendar_event_id)
        if not orders:
            return
        order_dates = orders.mapped("date_order")
        planner_summary = self.env["sale.planner.calendar.summary"]
        date_from = planner_summary._get_datetime_from_date_tz_hour(
            min(order_dates), self.env.company.sale_planner_order_cut_hour
        )
        date_to = planner_summary._get_datetime_from_date_tz_hour(
            max(order_dates), self.env.company.sale_planner_order_cut_hour
        ) + relativedelta(days=1)
        calendar_events = self.env["sale.planner.calendar.event"].search(
            [
                ("partner_id", "in", orders.partner_id.ids),
                ("user_id", "in", orders.user_id.ids),
                ("date", ">=", date_from),
                ("date", "<", date_to),
            ]
        )
        event_summaries = self.env["sale.planner.calendar.summary"].search(
            [
                ("user_id", "in", orders.user_id.ids),
                ("date", ">=", date_from.date()),
                ("date", "<", date_to.date()),
            ]
        )
        if not event_summaries:
            return
        cut_time = date_from.time()
        for order in orders:
            event = calendar_events.filtered(
                lambda ev: ev.partner_id == order.partner_id
                and ev.user_id == order.user_id
                and (ev.date.combine(ev.date.date(), cut_time) <= order.date_order)
                and (
                    ev.date.combine(ev.date.date(), cut_time) + relativedelta(days=1)
                    > order.date_order
                )
            )
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
                if not event_summary:
                    continue
                event_vals = order._prepare_calendar_event_planner()
                event_vals["calendar_summary_id"] = event_summary.id
                event = self.env["sale.planner.calendar.event"].create(event_vals)
            order.sale_planner_calendar_event_id = event
