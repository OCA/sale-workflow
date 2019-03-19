# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.v7
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids, context)
        return SaleOrder._amount_all(records, field_name, arg)

    @api.v8
    @api.depends('order_line.price_subtotal')
    def _amount_all_wrapper(self, field_name, arg):
        prev_values = dict()
        for order in self:
            prev_values.update(order.order_line.triple_discount_preprocess())
        res = super(SaleOrder, self)._amount_all(field_name, arg)
        self.env['sale.order.line'].triple_discount_postprocess(prev_values)
        return res
