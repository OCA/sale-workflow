# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo import _, api, fields, models, modules


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_calendar_events_domain(self):
        return [
            ("target_partner_id", "!=", False),
            ("sale_planner_state", "=", "pending"),
        ]

    @api.model
    def get_action_sale_planner_calendar_event(self):
        return self.env["ir.actions.act_window"]._for_xml_id(
            "sale_planner_calendar.action_sale_planner_calendar_event"
        )

    @api.model
    def systray_get_activities(self):
        res = super().systray_get_activities()
        datetime_now = fields.Datetime.now()
        domain = self._get_calendar_events_domain()
        start_date_today = fields.Datetime.to_string(
            datetime_now.replace(hour=0, minute=0, second=0)
        )
        end_date_today = fields.Datetime.to_string(
            datetime_now.replace(hour=23, minute=59, second=59)
        )
        domain_today = domain + [
            ("start", ">=", start_date_today),
            ("start", "<=", end_date_today),
        ]
        calendar_events_count_today = self.env["calendar.event"].search_count(
            domain_today
        )
        calendar_events_count_past = self.env["calendar.event"].search_count(
            domain + [("start", "<", start_date_today)]
        )
        calendar_events_count_future = self.env["calendar.event"].search_count(
            domain + [("start", ">", end_date_today)]
        )
        count_total = calendar_events_count_today + calendar_events_count_past
        if count_total:
            res.append(
                {
                    "id": self.env["ir.model"]._get("calendar.event").id,
                    "type": "activity",
                    "name": _("Calendar Events"),
                    "model": "calendar.event",
                    "icon": modules.module.get_module_icon(
                        self.env["calendar.event"]._original_module
                    ),
                    "total_count": count_total,
                    "today_count": calendar_events_count_today,
                    "overdue_count": calendar_events_count_past,
                    "planned_count": calendar_events_count_future,
                    "is_planner": True,
                    "domain": json.dumps(domain),
                }
            )
        return res
