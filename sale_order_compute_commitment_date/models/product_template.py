# Copyright 2025 APSL Nagarro
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    attribute_extend_lead_time = fields.Boolean(
        help="If checked, the attribute lead time will be "
        "taken into account to calculate the final lead time.",
    )
