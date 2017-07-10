# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_order = fields.Boolean(
        string='Is Order',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('is_order', True),
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quotation Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
        help="For Sales Order, this field references to its Quotation",
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Order Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
        help="For Quotation, this field references to its Sales Order",
    )
    state2 = fields.Selection(
        [('draft', 'Draft'),
         ('sent', 'Mail Sent'),
         ('cancel', 'Cancelled'),
         ('done', 'Done'), ],
        string='Status',
        readonly=True,
        related='state',
        help="A dummy state used for quotation",
    )

    @api.model
    def create(self, vals):
        is_order = vals.get('is_order', False) or \
            self._context.get('is_order', False)
        if not is_order and vals.get('name', '/') == '/':
            Seq = self.env['ir.sequence']
            vals['name'] = Seq.next_by_code('sale.quotation') or '/'
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_convert_to_order(self):
        self.ensure_one()
        if self.is_order:
            raise UserError(
                _('Only quotation can convert to order'))
        Seq = self.env['ir.sequence']
        order = self.copy({
            'name': Seq.next_by_code('sale.order') or '/',
            'is_order': True,
            'quote_id': self.id,
            'client_order_ref': self.client_order_ref,
        })
        self.order_id = order.id  # Reference from this quotation to order
        if self.state in ('draft', 'sent'):
            self.action_done()
        return self.open_sale_order()

    @api.model
    def open_sale_order(self):
        return {
            'name': _('Sales Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'sale.order',
            'context': {'is_order': True, },
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': "[('is_order', '=', True)]",
            'res_id': self.order_id and self.order_id.id or False,
        }

    # noinspection PyMethodFirstArgAssignment
    @api.multi
    def action_confirm(self):
        for order in self:
            # The accept workflow of website_sale_quote does nothing else so
            # no return is suitable.  Other cases should not get here but
            # if so, difficult at this level to determine where the call came
            # from and what action is suitable.
            if not order.is_order:
                order.action_convert_to_order()
                self -= order
        if self:
            return super(SaleOrder, self).action_confirm()
        return True

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'website_id' in self._context:
            # mangle state fields
            # TODO Make this less fragile but only over alternative
            # was a big cut and paste from web Controller
            if args and args[-1] == ('state', 'in', ['sent', 'cancel']):
                args.append(('is_order', '=', False))
            elif args and args[-1] == ('state', 'in', ['sale', 'done']):
                args.append(('is_order', '=', True))
        return super(SaleOrder, self).search(args, offset=offset, limit=limit,
                                             order=order, count=count)
