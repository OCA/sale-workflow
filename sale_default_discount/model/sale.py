# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'discount': fields.float(
            'Default discount (%)',
            digits_compute=dp.get_precision('discount'),
            help='This discount is used by default when creating new lines',
        ),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result = super(SaleOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)

        if partner_id:
            partner = self.pool['res.partner'].browse(
                cr, uid, partner_id, context=context)
            if partner.sale_default_discount:
                result['value']['discount'] = partner.sale_default_discount

        return result
