# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#    Copyright 2016 Serpent Consulting Services Pvt. Ltd.
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

from openerp import models, fields, api, _
from openerp.exceptions import UserError

QUOTATION_STATES = ['draft', 'sent', 'sale']


class SaleOrderCancel(models.TransientModel):

    """ Ask a reason for the sale order cancellation."""
    _name = 'sale.order.cancel'
    _description = __doc__

    reason_id = fields.Many2one(
        'sale.order.cancel.reason',
        string='Reason',
        required=True)

    @api.one
    def confirm_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        sale_ids = self._context.get('active_ids')
        if sale_ids is None:
            return act_close
        assert len(sale_ids) == 1, "Only 1 sale ID expected"
        sale = self.env['sale.order'].browse(sale_ids)
        sale.cancel_reason_id = self.reason_id.id
        # in the official addons, they call the action_cancel()
        # but directly call action_cancel on sales orders
        if sale.state in QUOTATION_STATES:
            sale.action_cancel()
        else:
            raise UserError(
                _("You cannot cancel the"
                  " Quotation/Order in the current state!"))
        return act_close
