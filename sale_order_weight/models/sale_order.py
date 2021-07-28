# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_ordered_weight = fields.Float(
        compute='_compute_total_ordered_weight',
        string='Total Ordered Weight',
        store=True
    )
    total_delivered_weight = fields.Float(
        compute='_compute_total_delivered_weight',
        string='Total Delivered Weight',
        store=True
    )

    @api.depends('order_line.total_ordered_weight')
    def _compute_total_ordered_weight(self):
        for order in self:
            order.total_ordered_weight = sum(
                order.mapped('order_line.total_ordered_weight')
            )

    @api.depends('order_line.total_delivered_weight')
    def _compute_total_delivered_weight(self):
        for order in self:
            order.total_delivered_weight = sum(
                order.mapped('order_line.total_delivered_weight')
            )

    @api.multi
    def recalculate_weight(self):
        self.mapped('order_line')._onchange_weight()
