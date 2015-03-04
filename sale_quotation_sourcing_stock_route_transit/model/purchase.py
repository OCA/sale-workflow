# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
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
from openerp import models, api, exceptions, _


class Purchase(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _unconfirmed_sourced_sales(self):
        Sale = self.env['sale.order']
        po_lines = self.mapped('order_line')

        # accepted state is added to be compatible with
        # OCA/vertical-ngo/logistic_order
        unconfirmed_sales = Sale.search(
            [('order_line.sourced_by', 'in', po_lines.ids),
             ('state', 'in', ('draft', 'sent', 'accepted'))])
        return unconfirmed_sales

    @api.multi
    def wkf_confirm_order(self):
        """ Forbid confirmation of purchase order when there
        are unconfirmed sale orders sourced by its purchase lines
        """
        unconfirmed_sourced_sales = self._unconfirmed_sourced_sales()
        if unconfirmed_sourced_sales:
            raise exceptions.Warning(
                _("You cannot confirm the purchase order before confirming the"
                  " sales order(s) which use it as source. Currently the"
                  " following sales order(s) still needs confirmation:\n%s")
                % "\n".join(unconfirmed_sourced_sales.mapped('name')))
        return super(Purchase, self).wkf_confirm_order()
