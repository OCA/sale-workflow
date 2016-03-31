# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Opener B.V. (<https://opener.am>).
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
##############################################################################
from openerp import models, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def write(self, values):
        """ Propagate a modified delivery address to the procurement group,
        the pickings and stock moves.
        """
        res = super(SaleOrder, self).write(values)
        if 'partner_shipping_id' in values:
            for order in self:
                if not order.procurement_group_id or order.shipped:
                    continue
                for procurement in self.env['procurement.order'].search(
                        [('group_id', '=', order.procurement_group_id.id)]):
                    if (procurement.location_id != order.partner_shipping_id
                            .property_stock_customer):
                        raise UserError(_(
                            'The delivery address can only be changed if '
                            'the related customer location remains the same.'))
                    procurement.write({'partner_dest_id':
                                       order.partner_shipping_id.id})
                pickings = order.picking_ids.filtered(
                    lambda picking: picking.state != 'done')
                pickings.write(
                    {'partner_id': order.partner_shipping_id.id})
                pickings.mapped('move_lines').write(
                    {'partner_id': order.partner_shipping_id.id})
        return res
