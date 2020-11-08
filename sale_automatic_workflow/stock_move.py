# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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
##############################################################################

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        res = super(StockMove, self)._picking_assign(procurement_group,
                                                     location_from,
                                                     location_to)

        sale_obj = self.env['sale.order']
        domain = [('procurement_group_id', '=', procurement_group)]
        sales = sale_obj.search(domain)
        # If we have several sales orders in one procurement group,
        # we group them in one picking. The possibilities when we have
        # several orders for one picking are:
        # 1. take the workflow of the first sale order
        # 2. do not propagate the workflow at all
        # 3. propagate the workflow if all the workflows are the same
        # The solution 1. is bad, the 3. could be hard to understand and
        # unpredictable. The solution 2. takes no assumption on what is
        # expected.
        if sales and len(sales) == 1:
            workflow = sales.workflow_process_id
            pickings = self.mapped('picking_id')
            pickings.write({'workflow_process_id': workflow.id})
        return res
