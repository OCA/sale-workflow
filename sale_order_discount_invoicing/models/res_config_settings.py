# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_split_discount_line = fields.Boolean(
        "Split Discount Lines",
        help="If set, a discounted sale line will be split in 2 invoice lines"
        " when the invoice is generated",
        related="company_id.account_split_discount_line",
        readonly=False,
    )
