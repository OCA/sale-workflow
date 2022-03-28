# Copyright 2021 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    partner_id = fields.Many2one(
        comodel_name="res.partner", related="order_id.partner_id",
    )
    date_order = fields.Datetime(
        related="order_id.date_order", string="Order Date", store=True, readonly=True,
    )
