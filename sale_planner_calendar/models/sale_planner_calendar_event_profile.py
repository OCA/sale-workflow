# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CalendarEventType(models.Model):
    """
    Calendar planner event profiles are used to categorise such events. Each type is a
    type of activity, e.g. face-to-face, telephone, message. This will allow an icon
    identifying the event to be displayed
    """

    _name = "sale.planner.calendar.event.profile"
    _description = "Sale Planner Calendar Event Profile"

    name = fields.Char(required=True)
    icon = fields.Char(help="Font awesome icon e.g. fa-tasks")
