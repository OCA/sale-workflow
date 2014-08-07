# -*- coding: utf-8 -*-
#
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
#

from openerp.osv import orm


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        vals = super(sale_order, self).onchange_partner_id(
            cr, uid, ids, part, context=context)
        if not part:
            return vals
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, part, context=context)
        if partner.use_prepayment:
            vals['value']['order_policy'] = 'prepaid'
        return vals
