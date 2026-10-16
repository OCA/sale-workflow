# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.stock.models import stock_move


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    priority = fields.Selection(stock_move.PROCUREMENT_PRIORITIES, default="0")
