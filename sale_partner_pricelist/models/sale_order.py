# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_allowed_pricelist_ids = fields.Many2many(
        related="partner_id.commercial_partner_id.allowed_pricelist_ids"
    )
