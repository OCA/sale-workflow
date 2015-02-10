# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle, Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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

from openerp import exceptions


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def final_destination(self):
        """Find the destination of the final chained move to the procurement.

        This will take into account the move that generated the current
        procurement through procurement rules. However, it will not take into
        account push rules.

        """
        self.ensure_one()
        move = self.move_dest_id
        if move:
            while move.move_dest_id:
                move = move.move_dest_id
            return move.location_dest_id
        else:
            return self.location_id

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

            sale_line = (
                procurement.sale_line_id or
                procurement.move_dest_id.procurement_id.sale_line_id or
                False
            )

            if sale_line and sale_line.manually_sourced:
                po_line = sale_line.sourced_by

                if (po_line.order_id.location_id
                        != procurement.final_destination()):
                    message = _(
                        'The manually sourced Purchase Order has Destination '
                        'location {}, while the Procurement (or the chained '
                        'moves) have destination {}. To solve the problem, '
                        'please source a Sale Order Line with a '
                        'Purchase Order consistent with the active Route. '
                        'For example, if the active route is Drop Shipping, '
                        'the chosen PO should have destination location '
                        'Customers.'.format(
                            po_line.order_id.location_id.name,
                            procurement.final_destination().name
                        )
                    )
                    if 'foreground_procurement' in self.env.context:
                        raise exceptions.Warning(message)
                    else:
                        res[procurement.id] = False
                        procurement.message_post(body=message)
                else:
                    res[procurement.id] = po_line.id
                    procurement.purchase_line_id = po_line
                    procurement.message_post(body=_('Manually sourced'))
            else:
                to_propagate |= procurement
        res.update(super(ProcurementOrder, to_propagate).make_po())
        return res
