# Copyright 2026 Studio73
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_group_method_key = fields.Char(copy=False, readonly=True)
