# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_automatic_workflow for OpenERP                                        #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#    Copyright 2013 Camptocamp SA (Guewen Baconnier)
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################
from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = "sale.order"
    _columns = {
        'workflow_process_id': fields.many2one('sale.workflow.process',
                                               string='Workflow Process',
                                               ondelete='restrict'),
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        workflow = order.workflow_process_id
        if not workflow:
            return invoice_vals
        invoice_vals['workflow_process_id'] = workflow.id
        if workflow.invoice_date_is_order_date:
            invoice_vals['date_invoice'] = order.date_order
        return invoice_vals

    def _prepare_order_picking(self, cr, uid, order, context=None):
        picking_vals = super(sale_order, self)._prepare_order_picking(cr, uid, order, context=context)
        if order.workflow_process_id:
            picking_vals['workflow_process_id'] = order.workflow_process_id.id
        return picking_vals

    def onchange_payment_method_id(self, cr, uid, ids, payment_method_id, context=None):
        values = super(sale_order, self).onchange_payment_method_id(
            cr, uid, ids, payment_method_id, context=context)
        if not payment_method_id:
            return values
        method_obj = self.pool.get('payment.method')
        method = method_obj.browse(cr, uid, payment_method_id, context=context)
        workflow = method.workflow_process_id
        if workflow:
            values.setdefault('value', {})
            values['value']['workflow_process_id'] = workflow.id
        return values

    def onchange_workflow_process_id(self, cr, uid, ids, workflow_process_id, context=None):
        if not workflow_process_id:
            return {}
        result = {}
        workflow_obj = self.pool.get('sale.workflow.process')
        workflow = workflow_obj.browse(cr, uid, workflow_process_id, context=context)
        if workflow.picking_policy:
            result['picking_policy'] = workflow.picking_policy
        if workflow.order_policy:
            result['order_policy'] = workflow.order_policy
        if workflow.invoice_quantity:
            result['invoice_quantity'] = workflow.invoice_quantity
        return {'value': result}

    def test_create_invoice(self, cr, uid, ids):
        """ Workflow condition: test if an invoice should be created,
        based on the automatic workflow rules """
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1
            ids = ids[0]
        order = self.browse(cr, uid, ids)
        if order.order_policy != 'manual' or not order.workflow_process_id:
            return False
        invoice_on = order.workflow_process_id.create_invoice_on
        if invoice_on == 'on_order_confirm':
            return True
        elif invoice_on == 'on_picking_done' and order.shipped:
            return True
        return False
