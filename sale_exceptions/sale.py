# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LTDA.
#    Copyright (C) 2010-2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Copyright (C) 2012 Camptocamp SA (Guewen Baconnier)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import netsvc

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.osv.osv import except_osv
from tools.safe_eval import safe_eval as eval
from tools.translate import _

class sale_exception(Model):
    _name = "sale.exception"
    _description = "Sale Exceptions"
    _columns = {
        'name': fields.char('Exception Name', size=64, required=True, translate=True),
        'description': fields.text('Description', translate=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when applying the test"),
        'model': fields.selection([('sale.order', 'Sale Order'),
                                   ('sale.order.line', 'Sale Order Line')],
                                  string='Apply on', required=True),
        'active': fields.boolean('Active'),
        'code': fields.text('Python Code',
                    help="Python code executed to check if the exception apply or not. " \
                         "The code must apply block = True to apply the exception."),
        'sale_order_ids': fields.many2many('sale.order', 'sale_order_exception_rel',
                                           'exception_id', 'sale_order_id',
                                           string='Sale Orders', readonly=True),
    }

    _defaults = {
        'code': """# Python code. Use failed = True to block the sale order.
# You can use the following variables :
#  - self: ORM model of the record which is checked
#  - order or line: browse_record of the sale order or sale order line
#  - object: same as order or line, browse_record of the sale order or sale order line
#  - pool: ORM model pool (i.e. self.pool)
#  - time: Python time module
#  - cr: database cursor
#  - uid: current user id
#  - context: current context
"""
    }

class sale_order(Model):
    _inherit = "sale.order"

    _order = 'main_exception_id asc, date_order desc, name desc'

    def _get_main_error(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sale_order in self.browse(cr, uid, ids, context=context):
            if sale_order.state == 'draft' and sale_order.exceptions_ids:
                res[sale_order.id] = sale_order.exceptions_ids[0].id
            else:
                res[sale_order.id] = False
        return res

    _columns = {
        'main_exception_id': fields.function(_get_main_error,
                        type='many2one',
                        relation="sale.exception",
                        string='Main Exception',
                        store={
                            'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['exceptions_ids', 'state'], 10),
                        }),
        'exceptions_ids': fields.many2many('sale.exception', 'sale_order_exception_rel',
                                           'sale_order_id', 'exception_id',
                                           string='Exceptions'),
        'ignore_exceptions': fields.boolean('Ignore Exceptions'),
    }

    def test_all_draft_orders(self, cr, uid, context=None):
        ids = self.search(cr, uid, [('state', '=', 'draft')])
        self.test_exceptions(cr, uid, ids)
        return True

    def _popup_exceptions(self, cr, uid, order_id, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        list_obj = self.pool.get('sale.exception.confirm')
        ctx = context.copy()
        ctx.update({'active_id': order_id,
                    'active_ids': [order_id]})
        list_id = list_obj.create(cr, uid, {}, context=ctx)
        view_id = model_data_obj.get_object_reference(
            cr, uid, 'sale_exceptions', 'view_sale_exception_confirm')[1]
        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.exception.confirm',
            'view_id': [view_id],
            'target': 'new',
            'nodestroy': True,
            'res_id': list_id,
        }
        return action

    def button_order_confirm(self, cr, uid, ids, context=None):
        exception_ids = self.detect_exceptions(cr, uid, ids, context=context)
        if exception_ids:
            return self._popup_exceptions(cr, uid, ids[0],  context=context)
        else:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        return True

    def test_exceptions(self, cr, uid, ids, context=None):
        """
        Condition method for the workflow from draft to confirm
        """
        exception_ids = self.detect_exceptions(cr, uid, ids, context=context)
        if exception_ids:
            return False
        return True

    def detect_exceptions(self, cr, uid, ids, context=None):
        exception_obj = self.pool.get('sale.exception')
        order_exception_ids = exception_obj.search(cr, uid,
            [('model', '=', 'sale.order')], context=context)
        line_exception_ids = exception_obj.search(cr, uid,
            [('model', '=', 'sale.order.line')], context=context)

        order_exceptions = exception_obj.browse(cr, uid, order_exception_ids, context=context)
        line_exceptions = exception_obj.browse(cr, uid, line_exception_ids, context=context)

        exception_ids = False
        for order in self.browse(cr, uid, ids):
            if order.ignore_exceptions:
                continue
            exception_ids = self._detect_exceptions(cr, uid, order,
                order_exceptions, line_exceptions, context=context)

            self.write(cr, uid, [order.id], {'exceptions_ids': [(6, 0, exception_ids)]})
        return exception_ids

    def _exception_rule_eval_context(self, cr, uid, obj_name, obj, context=None):
        if context is None:
            context = {}

        return {obj_name: obj,
                'self': self.pool.get(obj._name),
                'object': obj,
                'obj': obj,
                'pool': self.pool,
                'cr': cr,
                'uid': uid,
                'user': self.pool.get('res.users').browse(cr, uid, uid),
                'time': time,
                # copy context to prevent side-effects of eval
                'context': dict(context),}

    def _rule_eval(self, cr, uid, rule, obj_name, obj, context):
        expr = rule.code
        space = self._exception_rule_eval_context(cr, uid, obj_name, obj,
                                                  context=context)
        try:
            eval(expr, space,
                 mode='exec', nocopy=True) # nocopy allows to return 'result'
        except Exception, e:
            raise except_osv(_('Error'), _('Error when evaluating the sale exception rule :\n %s \n(%s)') %
                                 (rule.name, e))
        return space.get('failed', False)

    def _detect_exceptions(self, cr, uid, order, order_exceptions, line_exceptions, context=None):
        exception_ids = []
        for rule in order_exceptions:
            if self._rule_eval(cr, uid, rule, 'order', order, context):
                exception_ids.append(rule.id)

        for order_line in order.order_line:
            for rule in line_exceptions:
                if rule.id in exception_ids:
                    continue  # we do not matter if the exception as already been
                    # found for an order line of this order
                if self._rule_eval(cr, uid, rule, 'line', order_line, context):
                    exception_ids.append(rule.id)

        return exception_ids

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'ignore_exceptions': False,
        })
        return super(sale_order, self).copy(cr, uid, id, default=default, context=context)
