# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Authors: Raphaël Valyi, Renato Lima
#    Copyright (C) 2011 Akretion LTDA.
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
#

import time

from openerp import api, models, fields
from openerp.exceptions import except_orm
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _


class SaleException(models.Model):
    _name = 'sale.exception'
    _description = "Sale Exceptions"
    _order = 'active desc, sequence asc'

    name = fields.Char('Exception Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when applying the test")
    model = fields.Selection(
        [('sale.order', 'Sale Order'),
         ('sale.order.line', 'Sale Order Line')],
        string='Apply on', required=True)
    active = fields.Boolean('Active')
    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. The code must apply block = True to apply the "
             "exception.",
        default="""
# Python code. Use failed = True to block the sale order.
# You can use the following variables :
#  - self: ORM model of the record which is checked
#  - order or line: browse_record of the sale order or sale order line
#  - object: same as order or line, browse_record of the sale order or
#    sale order line
#  - pool: ORM model pool (i.e. self.pool)
#  - time: Python time module
#  - cr: database cursor
#  - uid: current user id
#  - context: current context
""")
    sale_order_ids = fields.Many2many(
        'sale.order',
        'sale_order_exception_rel', 'exception_id', 'sale_order_id',
        string='Sale Orders',
        readonly=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _order = 'main_exception_id asc, date_order desc, name desc'

    main_exception_id = fields.Many2one(
        'sale.exception',
        compute='_get_main_error',
        string='Main Exception',
        store=True)
    exception_ids = fields.Many2many(
        'sale.exception',
        'sale_order_exception_rel', 'sale_order_id', 'exception_id',
        string='Exceptions')

    ignore_exceptions = fields.Boolean('Ignore Exceptions')

    @api.one
    @api.depends('state', 'exception_ids')
    def _get_main_error(self):
        if self.state == 'draft' and self.exception_ids:
            self.main_exception_id = self.exception_ids[0]
        else:
            self.main_exception_id = False

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.one
    def _popup_exceptions(self):
        model_data_obj = self.env['ir.model.data']
        list_obj = self.env['sale.exception.confirm']
        list_id = (list_obj
                   .with_context(active_id=self.ids[0],
                                 active_ids=self.ids)
                   .create({}))
        view_id = model_data_obj.get_object_reference(
            'sale_exceptions', 'view_sale_exception_confirm')[1]
        action = {
            'name': _("Blocked in draft due to exceptions"),
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

    @api.one
    def action_button_confirm(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def test_exceptions(self):
        """
        Condition method for the workflow from draft to confirm
        """
        if self.detect_exceptions():
            return False
        return True

    @api.multi
    def detect_exceptions(self):
        """returns the list of exception_ids for all the considered sale orders

        as a side effect, the sale order's exception_ids column is updated with
        the list of exceptions related to the SO
        """
        exception_obj = self.env['sale.exception']
        order_exceptions = exception_obj.search(
            [('model', '=', 'sale.order')])
        line_exceptions = exception_obj.search(
            [('model', '=', 'sale.order.line')])

        all_exception_ids = []
        for order in self:
            if order.ignore_exceptions:
                continue
            exception_ids = order._detect_exceptions(order_exceptions,
                                                     line_exceptions)
            order.exception_ids = [(6, 0, exception_ids)]
            all_exception_ids += exception_ids
        return all_exception_ids

    @api.model
    def _exception_rule_eval_context(self, obj_name, rec):
        user = self.env['res.users'].browse(self._uid)
        return {obj_name: rec,
                'self': self.pool.get(rec._name),
                'object': rec,
                'obj': rec,
                'pool': self.pool,
                'cr': self._cr,
                'uid': self._uid,
                'user': user,
                'time': time,
                # copy context to prevent side-effects of eval
                'context': self._context.copy()}

    @api.model
    def _rule_eval(self, rule, obj_name, rec):
        expr = rule.code
        space = self._exception_rule_eval_context(obj_name, rec)
        try:
            safe_eval(expr,
                      space,
                      mode='exec',
                      nocopy=True)  # nocopy allows to return 'result'
        except Exception, e:
            raise except_orm(
                _('Error'),
                _('Error when evaluating the sale exception '
                  'rule:\n %s \n(%s)') % (rule.name, e))
        return space.get('failed', False)

    @api.one
    def _detect_exceptions(self, order_exceptions,
                           line_exceptions):
        exception_ids = []
        for rule in order_exceptions:
            if self._rule_eval(rule, 'order', self):
                exception_ids.append(rule.id)

        for order_line in self.order_line:
            for rule in line_exceptions:
                if rule.id in exception_ids:
                    # we do not matter if the exception as already been
                    # found for an order line of this order
                    continue
                if self._rule_eval(rule, 'line', order_line):
                    exception_ids.append(rule.id)
        return exception_ids

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'ignore_exceptions': False,
        })
        return super(SaleOrder, self).copy(default=default)
