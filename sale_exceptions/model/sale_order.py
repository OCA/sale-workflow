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

    @api.multi
    def _popup_exceptions(self):
        model_data_model = self.env['ir.model.data']
        wizard_model = self.env['sale.exception.confirm']

        new_context = {'active_id': self.ids[0], 'active_ids': self.ids}
        wizard = wizard_model.with_context(new_context).create({})

        view_id = model_data_model.get_object_reference(
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
            'res_id': wizard.id,
        }
        return action

    @api.multi
    def action_button_confirm(self):
        self.ensure_one()
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

    @api.multi
    def _detect_exceptions(self, order_exceptions,
                           line_exceptions):
        self.ensure_one()
        exception_ids = set()
        for rule in order_exceptions:
            if self._rule_eval(rule, 'order', self):
                exception_ids.add(rule.id)

        for order_line in self.order_line:
            for rule in line_exceptions:
                if self._rule_eval(rule, 'line', order_line):
                    order_line.exception_ids |= rule
                    exception_ids.add(rule.id)
                else:
                    order_line.exception_ids -= rule
        return list(exception_ids)

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'ignore_exceptions': False,
        })
        return super(SaleOrder, self).copy(default=default)
