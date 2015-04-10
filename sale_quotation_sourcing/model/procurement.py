# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle, Leonardo Pistone
#    Copyright 2014-2015 Camptocamp SA
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
from openerp import models, api, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        """
        link the procurement to the PO line sourcing the SO line
        if the SO line is manually sourced. Otherwise, use the normal
        implementation.
        """
        res = {}
        to_propagate = self.browse()
        for procurement in self:
            curr_proc = procurement
            sale_line = False
            while curr_proc:
                if curr_proc.sale_line_id:
                    sale_line = curr_proc.sale_line_id
                    break
                curr_proc = curr_proc.move_dest_id.procurement_id

            if sale_line and sale_line.manually_sourced:
                po_line = sale_line.sourced_by
                res[procurement.id] = po_line.id
                procurement.purchase_line_id = po_line
                procurement.message_post(body=_('Manually sourced'))
            else:
                to_propagate |= procurement
        res.update(super(ProcurementOrder, to_propagate).make_po())
        return res
