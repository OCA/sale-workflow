# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class sale(orm.Model):
    _inherit = 'sale.order'

    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        """Copied form the original function. Remove the default
        value for price list. Price list can be configured for each partner."""
        context = context or {}
        res = super(sale, self).onchange_shop_id(
            cr, uid, ids, shop_id, context=context)
        if 'pricelist_id' in res['value']:
            del res['value']['pricelist_id']
        return res
