# -*- coding: utf-8 -*-
# © 2015 Stefan Rijnhart - Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
