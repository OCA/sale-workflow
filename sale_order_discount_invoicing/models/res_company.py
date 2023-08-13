# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_split_discount_line = fields.Boolean(
        "Split Discount Lines",
        default=False,  # Do not set to True, else Odoo/OCB tests will fail
    )
