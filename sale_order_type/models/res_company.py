# Copyright 2025 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_type_required = fields.Boolean(
        default=True, help="If checked, the sale orders will require a type."
    )
