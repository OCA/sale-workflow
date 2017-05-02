# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2012 Ecosoft (<http://www.ecosoft.co.th>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(
        [('quotation', 'Quotation'),
         ('sale_order', 'Sales Order'), ],
        string='Order Type',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('order_type', 'sale_order'),
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quotation Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
        help="For Sales Order, this field reference to its Quotation",
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Order Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
        help="For Quotation, this field reference to its Sales Order",
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
        order_type = vals.get('order_type', False) or \
            self._context.get('order_type', False)
        if order_type == 'quotation' and vals.get('name', '/') == '/':
            Seq = self.env['ir.sequence']
            vals['name'] = Seq.next_by_code('sale.quotation') or '/'
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_convert_to_order(self):
        self.ensure_one()
        if self.order_type != 'quotation':
            raise UserError(
                _('Only quotation is allowed to convert to order!'))
        Seq = self.env['ir.sequence']
        order = self.copy({
            'name': Seq.next_by_code('sale.order') or '/',
            'order_type': 'sale_order',
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
            'context': {'order_type': 'sale_order', },
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': "[('order_type', '=', 'sale_order')]",
            'res_id': self.order_id and self.order_id.id or False,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
