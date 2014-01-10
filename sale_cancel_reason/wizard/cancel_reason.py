# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

from openerp.osv import orm, fields
from openerp import netsvc


class logistic_requisition_cancel(orm.TransientModel):
    """ Ask a reason for the sale order cancellation."""
    _name = 'sale.order.cancel'
    _description = __doc__

    quotation_states = ['draft', 'sent']

    _columns = {
        'reason_id': fields.many2one('sale.order.cancel.reason',
                                     string='Reason',
                                     required=True),
    }

    def confirm_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "1 ID expected"
            ids = ids[0]
        act_close = {'type': 'ir.actions.act_window_close'}
        sale_ids = context.get('active_ids')
        if sale_ids is None:
            return act_close
        assert len(sale_ids) == 1, "Only 1 sale ID expected"
        form = self.browse(cr, uid, ids, context=context)
        sale_obj = self.pool.get('sale.order')
        sale_obj.write(cr, uid, sale_ids,
                       {'cancel_reason_id': form.reason_id.id},
                       context=context)
        sale = sale_obj.browse(cr, uid, sale_ids[0], context=context)
        # in the official addons, they call the signal on quotations
        # but directly call action_cancel on sales orders
        if sale.state in self.quotation_states:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order',
                                    sale_ids[0], 'cancel', cr)
        else:
            sale_obj.action_cancel(cr, uid, sale_ids, context=context)
        return act_close
