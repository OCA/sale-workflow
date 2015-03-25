# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_order_type(self):
        return self.env['sale.order.type'].search([])[:1]

    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', default=_get_order_type)

    @api.multi
    def on_change_type_id(self, type_id):
        if type_id:
            type = self.env['sale.order.type'].browse(type_id)
            return {'value': {'warehouse_id': type.warehouse_id.id}}
        return {}

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            type = self.env['sale.order.type'].browse(vals['type_id'])
            if type.sequence_id:
                sequence_obj = self.env['ir.sequence']
                vals['name'] = sequence_obj.next_by_id(type.sequence_id.id)
        return super(SaleOrder, self).create(vals)

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(SaleOrder, self)._prepare_invoice(order, line_ids)
        res['journal_id'] = order.type_id.journal_id.id
        return res
