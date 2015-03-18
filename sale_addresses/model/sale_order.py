# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher, Leonardo Pistone
#    Copyright 2014-2015 Camptocamp SA
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
from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    origin_address_id = fields.Many2one(
        'res.partner',
        string='Origin Address',
        readonly=True,
        compute='_origin_address',
        help='The place from which the shipment will be sent',
        )

    @api.depends('order_id.warehouse_id',
                 'route_id',
                 'order_id.company_id.partner_id')
    @api.one
    def _origin_address(self):
        if self.route_id:
            address = self.env['res.partner']
        elif self.order_id.warehouse_id.partner_id:
            address = self.order_id.warehouse_id.partner_id
        else:
            address = self.order_id.company_id.partner_id
        self.origin_address_id = address


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    LO_STATES = {
        'cancel': [('readonly', True)],
        'progress': [('readonly', True)],
        'manual': [('readonly', True)],
        'shipping_except': [('readonly', True)],
        'invoice_except': [('readonly', True)],
        'done': [('readonly', True)],
    }

    consignee_id = fields.Many2one(
        'res.partner',
        string='Consignee',
        states=LO_STATES,
        help="The person to whom the shipment is to be delivered.")

    @api.model
    def _prepare_procurement_group(self, order):
        res = super(SaleOrder, self)._prepare_procurement_group(order)
        res.update({'consignee_id': order.consignee_id.id,
                    })
        return res

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id)
        res['origin_address_id'] = line.origin_address_id.id
        return res
