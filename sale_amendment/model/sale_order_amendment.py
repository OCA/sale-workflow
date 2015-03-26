# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, exceptions, _


class SaleOrderAmendment(models.TransientModel):
    _name = 'sale.order.amendment'

    sale_id = fields.Many2one(comodel_name='sale.order',
                              string='Sale Order',
                              required=True,
                              readonly=True)
    item_ids = fields.One2many(comodel_name='sale.order.amendment.item',
                               inverse_name='amendment_id',
                               string='Items')
    reason = fields.Html()

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderAmendment, self).default_get(fields)
        sale_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')

        if not sale_ids or len(sale_ids) != 1:
            return res
        assert active_model == 'sale.order', 'Bad context propagation'

        sale = self.env['sale.order'].browse(sale_ids)

        if sale.order_policy != 'picking' and sale.invoice_ids:
            raise exceptions.Warning(
                _('An invoiced order cannot be amended.')
            )

        items = []
        for line in sale.order_line:
            if line.state == 'cancel':
                continue
            items.append(self._prepare_item(line))
        res['item_ids'] = items
        return res

    @api.model
    def _prepare_item(self, sale_line):
        ordered = sale_line.product_uom_qty

        shipped = 0.
        canceled = 0.
        for procurement in sale_line.procurement_ids:
            if procurement.state == 'done':
                shipped += procurement.product_qty
            elif procurement.state == 'cancel':
                canceled += procurement.product_qty

        amend = ordered - canceled - shipped
        return {
            'sale_line_id': sale_line.id,
            'shipped_qty': shipped,
            'canceled_qty': canceled,
            'amend_qty': amend,
        }

    @api.multi
    def _message_content(self):
        message = _("<h3>Reason for amending</h3><p>%s</p>") % self.reason
        return message

    @api.multi
    def do_amendment(self):
        self.ensure_one()
        sale = self.sale_id
        if self.reason:
            sale.message_post(body=self._message_content())
        return True

    @api.multi
    def wizard_view(self):
        view = self.env.ref('sale_amendment.view_sale_order_amendment')

        return {
            'name': _('Enter the amendment details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.amendment',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }


class SaleOrderAmendmentItem(models.TransientModel):
    _name = 'sale.order.amendment.item'

    amendment_id = fields.Many2one(comodel_name='sale.order.amendment',
                                   string='Amendment',
                                   required=True,
                                   readonly=True)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line',
                                   required=True,
                                   readonly=True)
    ordered_qty = fields.Float(related='sale_line_id.product_uom_qty')
    shipped_qty = fields.Float(string='Delivered',
                               readonly=True,
                               digits_compute=dp.get_precision('Product UoS'))
    canceled_qty = fields.Float(string='Canceled',
                                readonly=True,
                                digits_compute=dp.get_precision('Product UoS'))
    amend_qty = fields.Float(string='Amend',
                             digits_compute=dp.get_precision('Product UoS'))
    product_uom_id = fields.Many2one(related='sale_line_id.product_uom',
                                     readonly=True)

    @api.constrains('amend_qty')
    def _constrains_amend_qty(self):
        max_qty = self.ordered_qty - self.shipped_qty
        if self.amend_qty > max_qty:
            raise exceptions.ValidationError(
                _('The quantity cannot be larger than the original ordered '
                  'quantity for the product %s (maximum: %0.2f).') %
                (self.sale_line_id.name, max_qty)
            )
