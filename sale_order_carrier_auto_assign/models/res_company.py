# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    carrier_auto_assign = fields.Boolean(
        help="Enable carrier auto assign on sale order confirmation.",
    )
    carrier_on_create = fields.Boolean(
        help="On the sales quotation, add the shipping method on creation.",
    )
