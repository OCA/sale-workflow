# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp import models, api, fields


class MrpProduction(models.Model):
    """ Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'
    _service_product_lst = []
    _product_config_dict = {}

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = []
        for production in self:
            self = self.with_context(production_id=production.id)
            res = super(MrpProduction, self)._action_compute_lines(
                properties=properties)
        return res


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res = super(ProcurementOrder, self)._prepare_mo_vals(
            cr, uid, procurement, context=context)
        res['lot_id'] = procurement.sale_line_id.lot_id
        return res
