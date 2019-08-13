# Copyright 2011 Akretion, Camptocamp, Sodexis
# Copyright 2018 Akretion, Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('sale', 'Sale')],
    )
    model = fields.Selection(
        selection_add=[
            ('sale.order', 'Sale order'),
            ('sale.order.line', 'Sale order line'),
        ]
    )


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'base.exception']
    _name = 'sale.order'
    _order = 'main_exception_id asc, date_order desc, name desc'

    rule_group = fields.Selection(
        selection_add=[('sale', 'Sale')],
        default='sale',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    def _fields_trigger_check_exception(self):
        return ['ignore_exception', 'order_line', 'state']

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        check_exceptions = any(
            field in vals for field
            in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            record.sale_check_exception()
        return record

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        check_exceptions = any(
            field in vals for field
            in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            self.sale_check_exception()
        return result

    def sale_check_exception(self):
        orders = self.filtered(lambda s: s.state == 'sale')
        if orders:
            orders._check_exception()

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

    def _sale_get_lines(self):
        self.ensure_one()
        return self.order_line

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('sale_exception.action_sale_exception_confirm')
        return action
