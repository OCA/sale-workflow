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

from openerp import models, api

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def name_get(self):
        """ Add the PO number in the name"""
        res = []
        for line in self:
            name = "%s - %s (%s %s)" % (
                line.order_id.name,
                line.name,
                line.product_qty,
                line.product_uom.name)
            res.append((line.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """Do the name search on purchase order, bounded by args"""
        results = super(PurchaseOrderLine, self).name_search(
            name,
            args=args,
            operator=operator,
            limit=limit)
        if name and not results:
            domain = args + [('order_id.name', operator, name)]
            res = self.search(domain, limit=limit)
            results = res.name_get()
        return results
