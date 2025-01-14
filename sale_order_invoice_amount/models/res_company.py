# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    enable_amount_invoiced_based_on_quantity = fields.Boolean(
        string="Enable computing amount invoiced based on quantity",
        default=False,
    )
