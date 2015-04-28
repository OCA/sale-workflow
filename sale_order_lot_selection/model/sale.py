# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2015  Agile Business Group                              #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

from openerp import fields, models, api, _
from openerp.tools import float_compare


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.onchange('lot_id')
    def on_change_lot_id(self):
        res = {}
        warning = {}

        product_obj = self.env['product.product'].with_context(
            lot_id=self.lot_id.id).browse(self.lot_id.product_id.id)
        compare_qty = float_compare(product_obj.virtual_available,
                                    self.product_uom_qty,
                                    precision_rounding=(
                                        product_obj.uom_id.rounding))
        if compare_qty == -1:
            warn_msg = _('You plan to sell %.2f %s but you'
                         ' only have %.2f %s available !'
                         '\nThe real stock is %.2f %s.'
                         ' (without reservations)') % \
                        (self.product_uom_qty, product_obj.uom_id.name,
                            max(0, product_obj.virtual_available),
                            product_obj.uom_id.name,
                            max(0, product_obj.qty_available),
                            product_obj.uom_id.name)
            warning = {'title': _('Configuration Error!'),
                       'message': _(
                       "Not enough stock ! : ") + warn_msg + "\n\n"}
        res.update({'warning': warning})
        return res


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(
            sale_order, self)._prepare_order_line_procurement(
                order, line, group_id)
        res['lot_id'] = line.lot_id.id
        return res
