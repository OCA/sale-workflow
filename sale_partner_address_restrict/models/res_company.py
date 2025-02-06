# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_partner_address_restriction = fields.Boolean(
        help="Check this box if you want to restrict partner addresses selection "
        "in sale orders. They should depends on the Customer filled in."
    )
