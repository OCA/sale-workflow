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

from openerp import models, fields, api, _


class SaleOrderAmendment(models.TransientModel):
    _name = 'sale.order.amendment'

    sale_id = fields.Many2one(comodel_name='sale.order',
                              string='Sale Order',
                              required=True,
                              readonly=True)
    item_ids = fields.One2many(comodel_name='sale.order.amendment.item',
                               inverse_name='amendment_id',
                               string='Items')

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderAmendment, self).default_get(fields)
        sale_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')

        if not sale_ids or len(sale_ids) != 1:
            return res
        assert active_model == 'sale.order', 'Bad context propagation'

        sale = self.env['sale.order'].browse(sale_ids)
        items = []
        for line in sale.order_line:
            item = {
                'sale_line_id': line.id,
            }
            items.append(item)
        res['item_ids'] = items
        return res

    @api.multi
    def do_amendment(self):
        self.ensure_one()
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
    product_id = fields.Many2one(related='sale_line_id.product_id',
                                 readonly=True)
    ordered_qty = fields.Float(related='sale_line_id.product_uom_qty')
