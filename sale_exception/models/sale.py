# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import api, models, fields, _
from openerp.exceptions import UserError, ValidationError
from openerp.tools.safe_eval import safe_eval


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        [('sale', 'Sale')],
       )
    model = fields.Selection(
        [('sale.order', 'Sale order'),
        ('sale.order.line', 'Sale order line'), ])

class SaleOrder(models.Model):
    _inherit = ['sale.order', 'base.exception']
    _name = 'sale.order'
    _order = 'main_exception_id asc, date_order desc, name desc'

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.constrains('ignore_exception', 'order_line', 'state')
    def sale_check_exception(self):
        if self.state == 'sale':
            self._check_exception()

    @api.onchange('order_line')
    def onchange_ignore_exception(self):
        if self.state == 'sale':
            self.ignore_exception = False

    @api.multi
    def action_confirm(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def _sale_get_lines(self):
        self.ensure_one()
        return self.order_line
