# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging
from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import orm

logger = logging.getLogger(__name__)


class PriceList(orm.Model):
    _name = 'product.pricelist'
    _inherit = 'product.pricelist'

    def _get_allowed_product_ids(self, cr, uid, pricelist_id, context=None):
        plitems_obj = self.pool['product.pricelist.item']

        if context is None:
            context = {}

        date = (context.get('date') or
                datetime.utcnow().strftime(DEFAULT_SERVER_DATETIME_FORMAT))

        pool_plversion = self.pool['product.pricelist.version']
        pricelist_version_ids = pool_plversion.search(
            cr, uid, [
                ('pricelist_id', '=', pricelist_id),
                '|',
                ('date_start', '=', False),
                ('date_start', '<=', date),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', date),
            ],
            context=context)

        if not pricelist_version_ids:
            return []

        items = plitems_obj.search(
            cr, uid,
            [('price_version_id', 'in', pricelist_version_ids)],
            context=context
        )

        return plitems_obj._get_allowed_product_ids(cr, uid, items,
                                                    context=context)
