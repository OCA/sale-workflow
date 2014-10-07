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
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def name_get(self):
        """ Add the PO number in the name"""
        res = []
        for line in self:
            name = "%s - %s (%s %s)" % (line.order_id.name, 
                                     line.name,
                                     line.product_qty,
                                     line.product_uom.name)
            res.append((line.id,name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        results = super(PurchaseOrderLine, self).name_search(name, 
             args=args, operator=operator, limit=limit)
        if not results:
            po_obj = self.env['purchase.order']
            po_line_ids = []
            pos_found = po_obj.search([('name', operator, name)], limit=limit)
            for po in pos_found:
                for line in po.order_line:
                    po_line_ids.append(line.id)
            res = self.browse(po_line_ids)
            results = res.name_get()
        return results
