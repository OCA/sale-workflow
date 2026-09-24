# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_end_customer_id = fields.Many2one(
        "res.partner",
        string="End Customer",
        tracking=True,
        check_company=True,
    )
