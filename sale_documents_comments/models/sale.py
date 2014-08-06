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


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'comment': fields.text('Internal comments'),
        'propagated_comment': fields.text('Propagated internal comments'),
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res = super(SaleOrder, self)._prepare_invoice(cr, uid, order, lines,
                                                      context=context)
        if not 'sale_comment' in res:
            res['sale_comment'] = order.propagated_comment
        else:
            res['sale_comment'] += ' ' + order.propagated_comment
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        val = super(SaleOrder, self).onchange_partner_id(cr, uid, ids,
                                                         partner_id,
                                                         context=context)
        if partner_id:
            partner_obj = self.pool['res.partner']
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            val['value'].update(
                {'comment': partner.sale_comment,
                 'propagated_comment': partner.sale_propagated_comment})
        return val
