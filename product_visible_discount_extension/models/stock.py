# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import (
    models,
)


class StockMove(models.Model):

    """
    Subclass stock.move model.

    We have to subclass the stock.move model to copy
    discount information to invoices when invoices are
    created from delivery order.
    """

    _name = 'stock.move'
    _inherit = 'stock.move'

    def _get_invoice_line_vals(self, cr, uid, move,
                               partner, inv_type, context=None):
        """
        Copy visible_discount value to invoice line.

        When an invoice is created from a delivery order, it has to copy its
        visible_discount value from here.
        """
        base_method = super(StockMove, self)._get_invoice_line_vals
        res = base_method(cr, uid, move, partner, inv_type, context=context)
        if move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            res['visible_discount'] = sale_line.visible_discount

        return res
