# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo", ondelete="restrict"
    )
