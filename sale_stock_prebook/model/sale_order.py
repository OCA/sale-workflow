# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _
from openerp import SUPERUSER_ID

"""
* Pre-book stock while sale order is not yet confirmed.
    Create a stock move (without picking and procurement) to decrease virtual stock. That reservation gets updated with the sale order line.
    If a reservation is existing at order confirmation, use it in the generated picking.
"""

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
       'is_prebookable': fields.function(lambda self,*args,**kwargs:self._get_is_prebooked(*args,**kwargs), multi='prebooked',
                                         type='boolean', readonly=True,
                                         string='Stock Pre-bookable', help="Are there products pre-bookable?",
                                        ),
       'is_prebooked': fields.function(lambda self,*args,**kwargs:self._get_is_prebooked(*args,**kwargs), multi='prebooked',
                                       type='boolean', readonly=True,
                                       string='Stock Pre-booked', help="Are all products pre-booked in stock?",
                                       invisible=True,
                                       states={
                                        'draft':[('invisible',False)],
                                        'sent':[('invisible',False)],
                                       },
                                      ),
    }

    def _get_is_prebooked(self, cr, uid, ids, fields, args, context=None):
        """ Is pre-booked if foreach order lines it's mto or there is a stock move"""
        res={}
        for order_id in ids:
            res[order_id]={'is_prebookable':False,'is_prebooked':False}
        line_ids=map(sum,[x['order_line'] for x in self.read(cr,uid,ids,['order_line'],context=context)])
        for line in self.pool.get('sale.order.line').read(cr,uid,line_ids,['type','move_ids','order_id'],context=context,load='_classic_write'):
            if line['type']!='make_to_order':
                if line['move_ids']:
                    res[line['order_id']]['is_prebooked']=True
                else:
                    res[line['order_id']]['is_prebookable']=True
        return res
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """ Delete prebookings """
        unlink_ids=[]
        for line in order_lines:
            for move in line.move_ids:
                #we don't expect this method to be called outside quotation confirmation
                assert move._model._is_prebooked(move), _("Internal Error")
                unlink_ids.append(move.id)
        self._prebook_cancel(cr,uid,unlink_ids,context)
        return super(sale_order,self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id=picking_id, context=context)

    def button_prebook(self, cr, uid, ids, context):
        orders=self.read(cr,uid,ids,['is_prebookable'],context=context)
        if not reduce(lambda x,y:x or y,[x['is_prebookable'] for x in orders],False):
            raise osv.except_osv(_('Warning!'), _('All products are already pre-booked in stock.'))
        return {
            'name' : _('Pre-book products from stock'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.stock.prebook',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
    def button_prebook_cancel(self, cr, uid, ids, context):
        line_ids=map(sum,[x['order_line'] for x in self.read(cr,SUPERUSER_ID,ids,['order_line'],context=context)])
        self.pool.get('sale.order.line')._prebook_cancel(cr,uid,line_ids,context=context)

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
       'date_prebooked': fields.function(lambda self,*args,**kwargs:self._get_date_prebooked(*args,**kwargs), multi='prebooked',
                                         type='date', readonly=True,
                                         string='Pre-booked Stock Until',
                                         invisible=True,
                                         states={
                                          'draft':[('invisible',False)],
                                          'sent':[('invisible',False)],
                                         },
                                        ),
    }

    def _get_date_prebooked(self, cr, uid, ids, fields, args, context=None):
        res={}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id]={'date_prebooked':False}
            if line.move_ids:
                for move in line.move_ids:
                    if move._model._is_prebooked(move):
                        res[line.id]['date_prebooked']=move.date_validity
                        break
        return res

    def _prebook(self, cr, uid, ids, date_prebook, context=None):
        sale_obj=self.pool.get('sale.order')
        move_obj=self.pool.get('stock.move')
        for line in self.browse(cr,SUPERUSER_ID,ids,context=context):
            order=line.order_id
            picking_id=False
            date_planned = sale_obj._get_date_planned(cr, uid, order, line, order.date_order, context=context)
            d_move=sale_obj._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=None)
                #module sale_stock
                #   location_id = order.shop_id.warehouse_id.lot_stock_id.id
                #   output_id = order.shop_id.warehouse_id.lot_output_id.id
                #   return {
                #       'name': line.name,
                #       'picking_id': picking_id,
                #       'product_id': line.product_id.id,
                #       'date': date_planned,
                #       'date_expected': date_planned,
                #       'product_qty': line.product_uom_qty,
                #       'product_uom': line.product_uom.id,
                #       'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
                #       'product_uos': (line.product_uos and line.product_uos.id)\
                #               or line.product_uom.id,
                #       'product_packaging': line.product_packaging.id,
                #       'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                #       'location_id': location_id,
                #       'location_dest_id': output_id,
                #       'sale_line_id': line.id,
                #       'tracking_id': False,
                #       'state': 'draft',
                #       #'state': 'waiting',
                #       'company_id': order.company_id.id,
                #       'price_unit': line.product_id.standard_price or 0.0
                #   }
            d_move['state']='waiting' #ensure move don't get processed
            d_move['date_validity']=date_prebook
            if line.move_ids: #there are already moves linked to the line, don't create new one
                for move in line.move_ids:
                    assert move._model._is_prebooked(move), _("Internal Error")
                move_ids=[x['id'] for x in line.move_ids]
                move_obj.write(cr, uid, move_ids, d_move, context=context)
                subject="Updated pre-booking for %s"%line.name
            else:
                move_obj.create(cr, uid, d_move, context=context)
                subject="Pre-booking for %s"%line.name
            message="Stock has been pre-booked until %s"%date_prebook
            sale_obj.message_post(cr, uid, [order.id], subject=subject, body=message, context=context)
    def _prebook_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        sale_obj=self.pool.get('sale.order')
        move_ids=[]
        for line in self.browse(cr,SUPERUSER_ID,ids,context=context):
            move_ids+=[x['id'] for x in line.move_ids if x._model._is_prebooked(x)]
            subject="Cancelled pre-booking for %s"%line.name
            message="Stock pre-booking has been cancelled"
            sale_obj.message_post(cr, uid, [line.order_id.id], subject=subject, body=message, context=context)
        if move_ids:
            ctx=context.copy()
            ctx['call_unlink']=True #allow to delete non draft moves
            self.pool.get('stock.move').unlink(cr, uid, move_ids, context=ctx)

    def write(self, cr, uid, ids, vals, context=None):
        """Update pre-booking when line is changed"""
        res = super(sale_order_line,self).write(cr,uid,ids,vals,context=context)
        if vals.get('type','')=='make_to_order': #remove pre-booking if procurement method changed to mto
            self._prebook_cancel(cr,uid,ids,context=context)
        else: #update pre-booking if fields changed
            fields=['product_id','product_qty','product_uom','product_uos_qty','product_uos','product_packaging','partner_id','price_unit']
            if not set(vals.keys()).intersection(set(fields)):
                return res
            for line in self.read(cr,uid,ids,['date_prebooked'],context=context):
                if line['date_prebooked']:
                    self._prebook(cr,uid,[line['id']],line['date_prebooked'],context=context)
        return res

    #TODO: remove pre-booking if cancelled
    #def ...

    def button_prebook_update(self, cr, uid, ids, context):
        if context is None:
            context={}
        line=self.read(cr,uid,ids[0],['date_prebooked'],context=context)
        ctx=context.copy()
        ctx['default_date']=line['date_prebooked']
        return {
            'name' : _('Pre-book products from stock'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.stock.prebook',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }
    def button_prebook_cancel(self, cr, uid, ids, context):
        self._prebook_cancel(cr,uid,ids,context=context)

