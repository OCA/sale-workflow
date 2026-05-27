# Copyright 2026 Tecnativa - Carlos Roca
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    calendar_event_id = fields.Many2one(index=True)
