# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
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

from openerp import models, api


class Procurement(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        """Propagate owner from sale order line to stock move.

        This is run when a quotation is validated into a sale order.

        """
        res = super(Procurement, self)._run_move_create(procurement)
        sale_line = procurement.sale_line_id
        if sale_line:
            res['restrict_partner_id'] = sale_line.stock_owner_id.id
        return res
