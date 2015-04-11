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

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    comment = fields.Text(string='Internal comments')
    propagated_comment = fields.Text(string='Propagated internal comments')

    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(SaleOrder, self)._prepare_invoice(order, lines)
        if 'sale_comment' not in res:
            res['sale_comment'] = order.propagated_comment
        else:
            res['sale_comment'] += ' ' + (order.propagated_comment or '')
        return res

    @api.multi
    def onchange_partner_id(self, partner_id):
        val = super(SaleOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner_obj = self.env['res.partner']
            partner = partner_obj.browse(partner_id)
            comment = partner.sale_comment or ''
            p_comment = partner.sale_propagated_comment or ''
            if partner.parent_id:
                comment += '\n' + (partner.parent_id.sale_comment or '')
                p_comment += '\n' + (
                    partner.parent_id.sale_propagated_comment or '')
            val['value'].update({'comment': comment,
                                 'propagated_comment': p_comment})
        return val
