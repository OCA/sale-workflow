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

logger = logging.getLogger(__name__)

# Sentinel value to avoid passing the list of all existing products around
# when querying possible product ids for a pricelist.
ANY_PRODUCT = object()


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def search(self, cr, uid, args,
               offset=0, limit=None,
               order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get("pricelist"):
            pl_obj = self.pool["product.pricelist"]
            ctx = context.copy()
            pl_id = ctx.pop("pricelist")
            products = pl_obj._get_allowed_product_ids(cr, uid, pl_id,
                                                       context=ctx)
            if products is not ANY_PRODUCT:
                products = list(products)
                pl_len = len(products)
                args.append(("id", "in", products))
                logger.debug(
                    "Limiting product search by pricelist to %d items %r",
                    pl_len,
                    products[:10] + ["..."] if pl_len > 10 else products,
                )

        return super(ProductProduct, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
