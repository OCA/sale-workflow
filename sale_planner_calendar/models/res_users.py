# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from datetime import datetime

import pytz

from odoo import _, api, fields, models, modules


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_sale_planner_calendar_events_domain(self):
        return [
            ("user_id", "=", self.env.user.id),
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
        # Get user timezone or UTC if not set
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        # Get current time in user's timezone
        datetime_now = datetime.now(user_tz)
        domain = self._get_sale_planner_calendar_events_domain()
        # Start of day in user's timezone
        start_date_today_tz = datetime_now.replace(hour=0, minute=0, second=0)
        # Convert to UTC for domain
        start_date_today_utc = start_date_today_tz.astimezone(pytz.UTC)
        # End of day in user's timezone
        end_date_today_tz = datetime_now.replace(hour=23, minute=59, second=59)
        # Convert to UTC for domain
        end_date_today_utc = end_date_today_tz.astimezone(pytz.UTC)
        domain_today = domain + [
            ("start", ">=", fields.Datetime.to_string(start_date_today_utc)),
            ("start", "<=", fields.Datetime.to_string(end_date_today_utc)),
        ]
        events_today_count = self.env["calendar.event"].search_count(domain_today)
        events_overdue_count = self.env["calendar.event"].search_count(
            domain + [("start", "<", start_date_today_utc)]
        )
        events_planned_count = self.env["calendar.event"].search_count(
            domain + [("start", ">", end_date_today_utc)]
        )
        total_count = events_today_count + events_overdue_count
        if total_count:
            res.append(
                {
                    "id": self.env["ir.model"]._get("calendar.event").id,
                    "type": "activity",
                    "name": _("Sale planner calendar events"),
                    "model": "calendar.event",
                    "icon": modules.module.get_module_icon(
                        self.env["calendar.event"]._original_module
                    ),
                    "total_count": total_count,
                    "today_count": events_today_count,
                    "overdue_count": events_overdue_count,
                    "planned_count": events_planned_count,
                    "is_planner": True,
                    "domain": json.dumps(domain),
                }
            )
        return res
