# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    season_allowed_product_ids = fields.Many2many(
        related="order_id.season_allowed_product_ids"
    )
