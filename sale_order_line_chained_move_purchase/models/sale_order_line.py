# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    chained_purchase_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="related_sale_line_id",
    )
