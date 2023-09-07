# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_show_currency_rate = fields.Selection(
        [
            ("no", "No"),
            ("normal", "Normal"),
            ("inverse", "Inverse"),
            ("both", "Both"),
        ],
        string="Show Currency Rate",
        default="normal",
    )
