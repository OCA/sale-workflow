# Copyright 2021-2024 Tecnativa - Sergio Teruel
# Copyright 2021-2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CalendarEventType(models.Model):
    _inherit = "calendar.event.type"

    duration = fields.Float()
    icon = fields.Char(help="Font awesome icon e.g. fa-tasks")
