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

from openerp.osv import orm
from .product import ANY_PRODUCT

logger = logging.getLogger(__name__)


def build_q_tuple(cats, prods):
    if cats and prods:
        return ['&', ('categ_id', 'child_of', cats), ('id', 'in', prods)]
    elif cats:
        return [('categ_id', 'child_of', cats)]
    elif prods:
        return [('id', 'in', prods)]
    else:
        return []


def query_for_item(browse_item):
    return build_q_tuple(
        browse_item.categ_id and [browse_item.categ_id.id] or None,
        browse_item.product_id and [browse_item.product_id.id] or None,
    )


def or_queries(queries):
    res = []
    for q in queries[:-1]:
        res.append('|')
        res.extend(q)
    res.extend(queries[-1])
    return res


class PriceListItem(orm.Model):
    _name = 'product.pricelist.item'
    _inherit = 'product.pricelist.item'

    def _get_allowed_product_ids(self, cr, uid, ids, context=None):
        pricelist_obj = self.pool['product.pricelist']
        product_obj = self.pool['product.product']
        res = set()
        qs = []
        for item in self.browse(cr, uid, ids, context=context):
            if item.base == -1:
                pricelist = item.base_pricelist_id.id
                ids = pricelist_obj._get_allowed_product_ids(
                    cr, uid, pricelist, context=context)
                if item.categ_id or item.product_id:
                    subset = product_obj.search(
                        cr, uid,
                        query_for_item(item),
                        context=context)
                    if ids is ANY_PRODUCT:
                        res.update(subset)
                    res.update(set(subset) & set(ids))
                elif ids is ANY_PRODUCT:
                    return ANY_PRODUCT
                else:
                    res.update(ids)
            else:
                if item.categ_id or item.product_id:
                    qs.append(query_for_item(item))
                else:
                    return ANY_PRODUCT

        # Process pending, grouped searches
        if qs:
            query = or_queries(qs)
            res.update(product_obj.search(cr, uid, query, context=context))

        return res
