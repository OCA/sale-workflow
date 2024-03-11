# Copyright 2024 Ecosoft (<https://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    spread_on_sale = fields.Boolean(
        default=False,
        copy=False,
        help="Flag move line if spread is created from sales order,"
        "so it is not recomputed on posting",
    )
