# Copyright 2026 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_delivery_split_date = fields.Boolean(
        string="Split Deliveries by Date",
        help="Create one delivery per commitment date of the sale order lines.",
    )
