# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_state = fields.Selection([
        ('no', 'No delivery'),
        ('unprocessed', 'Unprocessed'),
        ('partially', 'Partially processed'),
        ('done', 'Done')],
        string='Delivery state',
        compute='compute_delivery_state',
        store=True
    )

    @api.depends('order_line', 'order_line.qty_delivered', 'state')
    def compute_delivery_state(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state in ('draft', 'cancel'):
                order.delivery_state = 'no'
            elif all((float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) >= 0 for line in order.order_line)):
                order.delivery_state = 'done'
            elif any((not float_is_zero(line.qty_delivered, precision_digits=precision) for line in order.order_line)):
                order.delivery_state = 'partially'
            else:
                order.delivery_state = 'unprocessed'
