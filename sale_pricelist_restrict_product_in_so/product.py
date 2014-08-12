# -*- encoding: utf-8 -*-
##############################################################################
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
##############################################################################

import logging

logger = logging.getLogger(__name__)

from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import orm


def get_pricelist_allowed_items(self, cr, uid, pricelist_id, context=None):
    """ Get the allowed categories or items for a pricelist
    Params:
    (self, cr, uid) -> common OE params
    pricelist_id    -> id of pricelist
    context         -> context dict

    Returns a list of (allowed_categories, allowed_products) where each is
    either a list of allowed item ids, or None for any"""
    if context is None:
        context = {}

    date = (context.get('date') or
            datetime.utcnow().strftime(DEFAULT_SERVER_DATETIME_FORMAT))

    pool_plversion = self.pool.['product.pricelist.version']
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

    pricelist_items_ids = [
        item_id
        for plversion in pool_plversion.read(
            cr, uid, pricelist_version_ids,
            fields=["items_id"], context=context
        )
        for item_id in plversion.get("items_id") or ()
    ]
    pool_plitem = self.pool['product.pricelist.item']
    res = []
    products = set()
    categories = set()
    for item in pool_plitem.read(cr, uid, pricelist_items_ids,
                                 fields=["base", "categ_id", "product_id"],
                                 context=context):
        # TODO check base == -1 for "Other pricelist",
        # for now we will assume that people.
        # this requires checking minimally for recursion
        if item["categ_id"] and item["product_id"]:
            res.append(([item["categ_id"][0]], [item["product_id"][0]]))
        elif item["categ_id"]:
            categories.add(item["categ_id"][0])
        elif item["product_id"]:
            products.add(item["product_id"][0])
        else:
            res.append((None, None))

    if products:
        res.append((None, list(products)))
    if categories:
        res.append((list(categories), None))

    return res


def build_q_tuple(cats, prods):
    if cats and prods:
        return ['&', ('categ_id', 'child_of', cats), ('id', 'in', prods)]
    elif cats:
        return [('categ_id', 'child_of', cats)]
    elif prods:
        return [('id', 'in', prods)]
    else:
        return []


def build_search_query(list_of_allowed):
    # no point in making a complex query if a pricelist allows everything
    if not list_of_allowed or (None, None) in list_of_allowed:
        return []

    res = []
    # we want to build a series of checks ('|', foo, '|', bar, baz) to
    # get the equivalent of (foo OR bar OR baz), so we add '|' before
    # each element, except the last one
    for cats, prods in list_of_allowed[:-1]:
        query = build_q_tuple(cats, prods)
        if query:
            res.append('|')
            res.extend(query)

    res.extend(build_q_tuple(*list_of_allowed[-1]))
    return res


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def search(self, cr, uid, args,
               offset=0, limit=None,
               order=None, context=None, count=False):
        if context is None:
            context = {}
        if context and "pricelist" in context:
            pl_args = build_search_query(
                get_pricelist_allowed_items(
                    self, cr, uid, context["pricelist"])
            )
            args.extend(pl_args)
            logger.debug("Adding search arguments for pricelist: %r", pl_args)

        return super(ProductProduct, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
