# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_rounding_line = fields.Boolean(
        default=False,
        help="Technical field used to identify the sale order line applied for rounding up totals.",
    )
