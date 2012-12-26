# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp.osv.orm import Model
from openerp.osv import fields

class stock_picking(Model):
    _inherit = "stock.picking"
    _columns = {
        'workflow_process_id':fields.many2one('sale.workflow.process', 'Sale Workflow Process'),
    }

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, \
                                                            inv_type, journal_id, context=context)
        invoice_vals['workflow_process_id'] = picking.workflow_process_id.id
        if picking.workflow_process_id.invoice_date_is_order_date:
            invoice_vals['date_invoice'] = picking.sale_id.date_order
        return invoice_vals

    def validate_picking(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context=context):
            self.force_assign(cr, uid, [picking.id])
            partial_data = {}
            for move in picking.move_lines:
                partial_data["move" + str(move.id)] = {'product_qty': move.product_qty, 
                                                       'product_uom': move.product_uom.id}
            self.do_partial(cr, uid, [picking.id], partial_data)
        return True

#TODO reimplement me
#    def validate_manufactoring_order(self, cr, uid, origin, context=None): #we do not create class mrp.production to avoid dependence with the module mrp
#        if context is None:
#            context = {}
#        wf_service = netsvc.LocalService("workflow")
#        mrp_prod_obj = self.pool.get('mrp.production')
#        mrp_product_produce_obj = self.pool.get('mrp.product.produce')
#        production_ids = mrp_prod_obj.search(cr, uid, [('origin', 'ilike', origin)])
#        for production in mrp_prod_obj.browse(cr, uid, production_ids):
#            mrp_prod_obj.force_production(cr, uid, [production.id])
#            wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce', cr)
#            context.update({'active_model': 'mrp.production', 'active_ids': [production.id], 'search_default_ready': 1, 'active_id': production.id})
#            produce = mrp_product_produce_obj.create(cr, uid, {'mode': 'consume_produce', 'product_qty': production.product_qty}, context)
#            mrp_product_produce_obj.do_produce(cr, uid, [produce], context)
#            self.validate_manufactoring_order(cr, uid, production.name, context)
#        return True
#        
