# coding: utf-8
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    blanket_order_id = fields.Many2one(
        'sale.blanket.order', string='Origin blanket order',
        related='order_line.blanket_line_id.order_id')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    blanket_line_id = fields.Many2one('sale.blanket.order.line')
