# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_manufacturing_order(self):
        model_data_obj = self.env['ir.model.data']
        action_obj = self.pool['ir.actions.act_window']
        prod_obj = self.env['mrp.production']

        action_id = model_data_obj .xmlid_to_res_id(
            'mrp.mrp_production_action')
        result = action_obj.read(self._cr, self._uid, action_id,
                                 context=self._context)
        mos = prod_obj.search([('sale_order_id', 'in', self.ids)])
        result['domain'] = [('id', 'in', mos.ids)]
        return result
