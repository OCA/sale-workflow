# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services (<http://www.serpentcs.com>)
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
############################################################################


import time
import operator
import itertools

from openerp import pooler
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.tools.translate import _


class ProductPricelist(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ProductPricelist, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_price_lines': self._get_price_lines,
            'get_active_version': self._get_active_version,
        })

    def _get_active_version(self, pricelist):
        date = self.localcontext.get('date') or time.strftime('%Y-%m-%d')
        versions = [
            version for version in pricelist.version_id
            if all((
                version.date_start is False or version.date_start <= date,
                version.date_end is False or version.date_end >= date,
            ))
        ]

        if not versions:
            raise orm.except_orm(
                _("Warning!"),
                _("At least one pricelist has no active version!"),
            )
        return versions[0]

    def _get_price_lines(self, pricelist, pricelist_version):
        """ Returns a list of (category_name, products) for a pricelist from a
        pricelist version browse record """
        # TODO: Allow looking through sub lists
        #     : Handle min quantity on categories
        pool = pooler.get_pool(self.cr.dbname)
        product_obj = pool.get("product.product")
        pricelist_obj = pool.get("product.pricelist")
        products_by_qty = set()
        for line in pricelist_version.items_id:
            min_qty = line.min_quantity
            domain = []
            if line.categ_id:
                domain.append(('categ_id', 'child_of', line.categ_id.id))
            if line.product_id:
                domain.append(('id', '=', line.product_id.id))

            products_by_qty.update(
                (product_id, min_qty)
                for product_id in product_obj.search(self.cr, self.uid, domain)
            )

        # In order to get prices, we call product_pricelist.price_get_multi:
        # Params: cr, uid, pricelist_ids, products_by_qty_by_partner, context
        # We currently don't pass in a partner, and we need to do one pass per
        # quantity per product because of the return structure
        # {product_id: {pricelist_id: price}}
        sale_price_digits = self.get_digits(dp='Product Price')
        prices = []
        pl_id = pricelist.id
        while products_by_qty:
            seen = set()
            prod_qty_map = {}
            arg, leftover = [], []
            for i in products_by_qty:
                if i[0] in seen:
                    leftover.append(i)
                else:
                    prod_qty_map[i[0]] = i[1]
                    arg.append((i[0], i[1], None))
                    seen.add(i[0])

            products_by_qty = leftover

            res = pricelist_obj.price_get_multi(self.cr, self.uid,
                                                [pl_id], arg,
                                                context=self.localcontext)
            res.pop("item_id", None)
            for product_id, price_dict in res.iteritems():
                prices.append(dict(
                    product_id=product_id,
                    min_qty=prod_qty_map[product_id],
                    price=self.formatLang(
                        price_dict[pl_id],
                        digits=sale_price_digits,
                        currency_obj=pricelist.currency_id,
                    ),
                ))

        # Now we have a bunch of product_ids, we need their info
        infos_dict = product_obj.read(
            self.cr, self.uid,
            [price["product_id"] for price in prices],
            ["name", "code", "categ_id", "id"],
        )
        infos_dict = dict((d["id"], d) for d in infos_dict)

        warn_ids = []
        for product in prices:
            info = infos_dict.get(product["product_id"])
            if not info:
                warn_ids.append(product["product_id"])
                continue

            product["category"] = info["categ_id"][1]
            product["name"] = info["name"]
            product["code"] = info["code"]

        prices.sort(key=operator.itemgetter("category", "name", "min_qty"))
        return itertools.groupby(prices, operator.itemgetter("category"))


report_sxw.report_sxw('report.webkit.pricelist_version_report',
                      'product.pricelist.version',
                      'addons/send_pricelist_by_email/report/pricelist_version_report.mako',
                      parser=ProductPricelist)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
