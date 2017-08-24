# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import chain

import time

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self,
                            products_qty_partner, date=False, uom_id=False):
        """ Have to copy the entire parent method because
        there is no simpler way to manage a new applied_on in pricelist.
        """
        self.ensure_one()
        context = self.env.context or {}
        date = context.get('date')
        if date:
            date = date[0:10]
        else:
            date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        products = map(lambda p: p[0], products_qty_partner)

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        price_categ_ids = [
            p.price_category_id.id for p in products if p.price_category_id
        ]

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in list(
                chain.from_iterable([t.product_variant_ids for t in products])
            )]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [
                product.product_tmpl_id.id for product in products
            ]

        # Load all rules
        self.env.cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s))'
            'AND (product_id IS NULL OR product_id = any(%s))'
            'AND (categ_id IS NULL OR categ_id = any(%s)) '
            'AND (price_category_id IS NULL OR price_category_id = any(%s)) '
            'AND (pricelist_id = %s) '
            'AND ((i.date_start IS NULL OR i.date_start <= %s) '
            'AND (i.date_end IS NULL OR i.date_end >= %s))'
            'ORDER BY applied_on, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, price_categ_ids,
             self.id, date, date))

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)

        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed
            # according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed
            # according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse(
                        [context['uom']]
                    )._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context,
                    # use default product UoM
                    pass

            # if Public user try to access standard price from website sale,
            # need to call _price_get.
            price = product.price_compute('list_price')[product.id]

            price_uom_id = qty_uom_id
            for rule in items:
                if rule.min_quantity \
                        and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id \
                            and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id:
                        if product.product_variant_count != 1:
                            # product rule acceptable on template
                            # if has only one variant
                            continue
                        else:
                            variant = product.product_variant_ids[0]
                            if variant.id != rule.product_id.id:
                                continue
                else:
                    if rule.product_tmpl_id:
                        tmpl_id = product.product_tmpl_id.id
                        if tmpl_id != rule.product_tmpl_id.id:
                            continue

                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.price_category_id:
                    if rule.price_category_id != product.price_category_id:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = self._price_get_multi(
                        rule.base_pricelist_id, [(product, qty, partner)]
                    )[product.id]
                    ptype_src = rule.base_pricelist_id.currency_id
                    price = ptype_src.compute(price_tmp,
                                              self.currency_id.id,
                                              round=False)
                else:
                    # if base option is public price take sale price
                    # else cost price of product
                    # price_get returns the price in the context UoM,
                    #  i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (
                    lambda price: product.uom_id._compute_price(
                        price, self.env['product.uom'].browse(price_uom_id)
                    )
                )

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price -
                                 (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price -
                                 (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(
                                price, precision_rounding=rule.price_round
                            )

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(
                                rule.price_surcharge
                            )
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(
                                rule.price_min_margin
                            )
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(
                                rule.price_max_margin
                            )
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' \
                    and suitable_rule.base != 'pricelist':
                price = product.currency_id.compute(
                    price, self.currency_id, round=False
                )

            results[product.id] = (
                price, suitable_rule and suitable_rule.id or False
            )
        return results


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    applied_on = fields.Selection(
        selection_add=[('2b_product_price_category', 'Price Category')]
    )

    price_category_id = fields.Many2one(
        comodel_name='product.price.category',
        string='Price Category',
        ondelete='cascade',
        help="Specify a product price category if this rule only applies "
             "to one price category. Keep empty otherwise."
    )

    @api.onchange('applied_on')
    def _onchange_applied_on_price_category(self):
        """ Reset the price_category_id value if applied_on
        is not price_category
        """
        if self.applied_on != '2b_product_price_category':
            self.price_category_id = False

    @api.depends('price_category_id')
    def _get_pricelist_item_name_price(self):
        """ Modify the computed name if pricelist item is applied on
        price category.
        """
        for rec in self:
            super(ProductPricelistItem, rec)._get_pricelist_item_name_price()
            if rec.price_category_id:
                rec.name = _("Price Category: %s") % rec.price_category_id.name
