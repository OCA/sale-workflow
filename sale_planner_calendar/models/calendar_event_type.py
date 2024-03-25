# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CalendarEventType(models.Model):
    _inherit = "calendar.event.type"

    duration = fields.Float()
