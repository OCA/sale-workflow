# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.procurement.models import procurement


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    priority = fields.Selection(
        procurement.PROCUREMENT_PRIORITIES, string='Priority', default='1')

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        res = super(SaleOrderLine, self) \
            ._prepare_order_line_procurement(group_id=group_id)
        res['priority'] = self.priority \
            or self.default_get(['priority'])['priority']
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    priority = fields.Selection(
        procurement.PROCUREMENT_PRIORITIES, string='Priority',
        compute='_compute_priority', inverse='_inverse_priority', store=True,
        index=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Priority for this sale order. "
             "Setting manually a value here would set it as priority "
             "for all the order lines")

    @api.multi
    @api.depends('order_line.priority')
    def _compute_priority(self):
        for order in self:
            priority = order.mapped('order_line.priority')
            order.priority = priority and max(priority) or '1'

    @api.multi
    def _inverse_priority(self):
        for order in self:
            priority = order.priority
            for line in order.order_line:
                line.priority = priority
