# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
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
from openerp.osv import orm


class ProcurementOrder(orm.Model):

    """
    Procurement Orders
    """
    _inherit = 'procurement.order'

    def is_service(self, cr, uid, ids):
        """ condition on the transition to go from 'confirm' activity to
        'confirm_wait' activity """
        for procurement in self.browse(cr, uid, ids):
            product = procurement.product_id
            if product.type == 'service':
                return True
        return False
