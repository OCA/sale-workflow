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
        default=lambda self: self._context.get('is_order', False),
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
        if self.state == 'draft':
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
