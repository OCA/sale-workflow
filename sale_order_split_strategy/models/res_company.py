# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_split_strategy_errors = fields.Selection(
        [
            ("raise_errors", "Raise errors"),
            ("post_message", "Post message"),
            ("do_nothing", "Do nothing"),
        ],
        required=True,
        default="raise_errors",
    )
