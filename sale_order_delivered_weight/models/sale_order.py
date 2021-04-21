# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_delivered_weight = fields.Float(
        compute='_compute_total_delivered_weight',
        string='Total Delivered Weight',
        store=True
    )

    @api.depends('order_line.qty_delivered')
    def _compute_total_delivered_weight(self):
        for order in self:
            total_delivered_weight = 0.0
            for line in order.order_line:
                total_delivered_weight += line.product_id.weight * line.qty_delivered
            order.total_delivered_weight = total_delivered_weight
