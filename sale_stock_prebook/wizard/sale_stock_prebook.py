# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
from openerp import SUPERUSER_ID

class sale_stock_prebook(osv.osv_memory):
    _name = 'sale.stock.prebook'
    _columns = {
        'date': fields.date("Pre-book stock until", help="Define date until when stock will be pre-booked", required=True),
    }
    def button_confirm(self, cr, uid, ids, context):
        wiz=self.browse(cr,uid,ids[0],context=context)
        if context['active_model']=='sale.order':
            order_line_ids=map(sum,[x['order_line'] for x in self.pool.get('sale.order').read(cr,uid,context['active_ids'],['order_line'],context=context,load='_classic_write')])
            self.pool.get('sale.order.line')._prebook(cr,uid,order_line_ids,wiz.date,context=context)
        elif context['active_model']=='sale.order.line':
            self.pool.get('sale.order.line')._prebook(cr,uid,context['active_ids'],wiz.date,context=context)
        return {'type': 'ir.actions.act_window_close'}
