# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Override price_unit to use Product Price Sales decimal precision
    price_unit = fields.Float(digits="Product Price Sales")
