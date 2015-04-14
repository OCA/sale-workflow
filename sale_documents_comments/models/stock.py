# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_comment = fields.Text(string='Internal comments')
    sale_propagated_comment = fields.Text(string='Propagated internal'
                                          ' comments')

    @api.one
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        picking_com = ''
        picking_pcom = ''
        if self.partner_id:
            picking_com = self.partner_id.picking_comment or ''
            picking_pcom = self.partner_id.picking_propagated_comment or ''
            parent = self.partner_id.parent_id
            if parent:
                picking_com += '\n' + (parent.picking_comment or '')
                picking_pcom += '\n' + (parent.picking_propagated_comment or
                                        '')
        self.sale_comment = picking_com
        self.sale_propagated_comment = picking_pcom

    @api.model
    def create(self, values):
        partner_id = values.get('partner_id', False)
        origin = values.get('origin', False)
        if partner_id:
            partner_obj = self.env['res.partner']
            if 'sale_comment' not in values:
                values['sale_comment'] = ''
            if 'sale_propagated_comment' not in values:
                values['sale_propagated_comment'] = ''
            if origin:
                sale_obj = self.env['sale.order']
                sale = sale_obj.search([('name', '=', origin)], limit=1)
                if sale:
                    if sale.propagated_comment:
                        values['sale_propagated_comment'] += (
                            sale.propagated_comment)
            partner = partner_obj.browse(partner_id)
            picking_com = partner.picking_comment or ''
            picking_pcom = partner.picking_propagated_comment or ''
            if partner.parent_id:
                picking_com += '\n' + (partner.parent_id.picking_comment or '')
                picking_pcom += ('\n' +
                                 (partner.parent_id.picking_propagated_comment
                                  or ''))
            if (picking_com and values['sale_comment'] != picking_com):
                values['sale_comment'] = (picking_com + '\n' +
                                          (values['sale_comment'] or ''))
            if (picking_pcom and
                    (values['sale_propagated_comment'] != picking_pcom)):
                values['sale_propagated_comment'] = (
                    picking_pcom + '\n' + (values['sale_propagated_comment'] or
                                           ''))
        return super(StockPicking, self).create(values)

    @api.model
    def _create_invoice_from_picking(self, picking, values):
        values['sale_comment'] = picking.sale_propagated_comment
        return super(StockPicking, self)._create_invoice_from_picking(picking,
                                                                      values)
