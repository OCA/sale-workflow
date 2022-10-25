# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import RedirectWarning
from odoo.tools.date_utils import relativedelta


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_sale_planner_contact = fields.Boolean()

    def action_calendar_planner(self):
        categ = self.env.ref("sale_planner_calendar.event_type_commercial_visit")
        action = self.env.ref("calendar.action_calendar_event").read()[0]
        sale_planner_forward_months = self.env.company.sale_planner_forward_months
        # TODO: Get default values from res.config.settings
        action["context"] = {
            "no_mail_to_attendees": False
            if self.env.company.sale_planner_mail_to_attendees
            else True,
            "calendar_event_primary_only": True,
            "default_target_partner_id": self.id,
            "default_categ_ids": [(4, categ.id)],
            "default_location": self._display_address(),
            "default_duration": categ.duration,
            "default_name": categ.name,
            "default_start": fields.Datetime.now(),
            "default_stop": fields.Datetime.now()
            + timedelta(minutes=round((categ.duration or 1.0) * 60)),
            "default_recurrency": True,
            "default_rrule_type": "weekly",
            "default_end_type": "end_date",
            "default_until": fields.Date.today()
            + relativedelta(months=sale_planner_forward_months),
            "default_is_dynamic_end_date": True,
            "default_user_id": self.user_id.id or self.env.user.id,
            "default_partner_ids": [
                (
                    6,
                    0,
                    [
                        self.id,
                        self.user_id.partner_id.id or self.env.user.partner_id.id,
                    ],
                )
            ],
        }
        action["view_mode"] = "tree,form"
        action["view_id"] = False
        action["views"] = []
        action["domain"] = [
            ("target_partner_id", "=", self.id),
            ("recurrency", "=", True),
            ("recurrence_id.until", ">", fields.Date.today()),
        ]
        return action

    def write(self, vals):
        if (
            "user_id" in vals
            and vals.get("user_id")
            and not self.env.context.get("skip_sale_planner_check", False)
        ):
            calendar_events = (
                self.env["calendar.event"]
                .with_context(calendar_event_primary_only=True)
                .search(
                    [
                        ("target_partner_id", "in", self.ids),
                        ("recurrency", "!=", False),
                        ("user_id", "!=", vals["user_id"]),
                    ]
                )
            )
            if calendar_events:
                action = self.env.ref(
                    "sale_planner_calendar.action_sale_planner_calendar_reassign_wiz"
                )
                msg = _(
                    "This partner has sale planned events\n"
                    "You must change salesperson from the planner wizard"
                )
                raise RedirectWarning(msg, action.id, _("Go to the planner wizard"))
        return super(ResPartner, self).write(vals)
