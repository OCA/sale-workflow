# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_manufacturing_order(self):
        model_data_obj = self.env['ir.model.data']
        action_obj = self.pool['ir.actions.act_window']
        prod_obj = self.env['mrp.production']

        action_id = model_data_obj .xmlid_to_res_id('mrp.mrp_production_action')

        result = action_obj.read(self._cr, self._uid, action_id,
                                 context=self._context)
        mos = prod_obj.search([('sale_order_id', 'in', self.ids)])
        result['domain'] = [('id', 'in', mos.ids)]
        return result
