# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class CalendarAttendee(models.Model):
    _inherit = "calendar.attendee"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.company.sale_planner_mail_to_attendees:
            new_vals_list = []
            for vals in vals_list:
                event = self.env["calendar.event"].browse(vals["event_id"])
                if not event.target_partner_id:
                    new_vals_list.append(vals)
            vals_list = new_vals_list
        return super().create(vals_list)
