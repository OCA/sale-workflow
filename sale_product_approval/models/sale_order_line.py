# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    approved_sale_confirm = fields.Boolean(
        related="product_id.sale_ok_confirm",
        string="Approved for Sale",
        store=True,
        default=True,
    )
