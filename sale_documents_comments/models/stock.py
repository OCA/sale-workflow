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

from openerp.osv import orm, fields


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'sale_comment': fields.text('Internal comments'),
        'sale_propagated_comment': fields.text('Propagated internal comments'),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not partner_id:
            return {}
        partner_obj = self.pool['res.partner']
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        value = {
            'sale_comment': partner.picking_comment,
            'sale_propagated_comment': partner.picking_propagated_comment,
        }
        return {'value': value}

    def create(self, cr, uid, values, context=None):
        partner_id = values.get('partner_id', False)
        origin = values.get('origin', False)
        if partner_id:
            partner_obj = self.pool['res.partner']
            if not 'sale_comment' in values:
                values['sale_comment'] = ''
            if not 'sale_propagated_comment' in values:
                values['sale_propagated_comment'] = ''
            if origin:
                sale_obj = self.pool['sale.order']
                sale_ids = sale_obj.search(cr, uid, [('name', '=', origin)],
                                           context=context)
                if sale_ids:
                    sale = sale_obj.browse(cr, uid, sale_ids[0],
                                           context=context)
                    if sale.propagated_comment:
                        values['sale_propagated_comment'] += (
                            sale.propagated_comment)
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            if partner.picking_comment and values['sale_comment'] != partner.picking_comment:
                values['sale_comment'] = (partner.picking_comment + '\n' +
                                          values['sale_comment'])
            if partner.picking_propagated_comment and (values['sale_propagated_comment'] !=
                    partner.picking_propagated_comment):
                values['sale_propagated_comment'] = (
                    partner.picking_propagated_comment + '\n' +
                    values['sale_propagated_comment'])
        return super(StockPicking, self).create(cr, uid, values,
                                                context=context)

    def _create_invoice_from_picking(self, cr, uid, picking, values,
                                     context=None):
        values['sale_comment'] = picking.sale_propagated_comment
        return super(StockPicking, self)._create_invoice_from_picking(
            cr, uid, picking, values, context=context)
