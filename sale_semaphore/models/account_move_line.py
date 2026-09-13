# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    semaphore = fields.Selection(
        [
            ("success", "🟢"),
            ("warning", "🟡"),
            ("danger", "🔴"),
        ],
    )
