# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, tools


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_price_from_supplierinfo(self, rule):
        sale_id = self._prefetch['sale.order']
        order = self.env['sale.order'].browse(sale_id)
        price = 0.0
        domain = [('id', 'in', self.seller_ids.ids)]
        if rule.min_quantity:
            domain += [('min_qty', '<=', rule.min_quantity)]
        if rule.date_start:
            domain += [('date_start', '>=', rule.date_start)]
        elif order and any(self.seller_ids.mapped('date_start')):
            domain += [('date_start', '>=', order.date_order)]
        if rule.date_end:
            domain += [('date_end', '<=', rule.date_end)]
        elif order and any(self.seller_ids.mapped('date_end')):
            domain += [('date_end', '>=', order.date_order)]
        item = self.env['product.supplierinfo'].search(domain, limit=1)
        if item:
            price = item.price
        if price:
            qty_uom_id = self._context.get('uom') or self.uom_id.id
            price_uom = self.env['product.uom'].browse([qty_uom_id])
            convert_to_price_uom = (
                lambda price: self.uom_id._compute_price(
                    price, price_uom))
            price_limit = price
            price = (price - (price * (rule.price_discount / 100))) or 0.0
            if rule.price_round:
                price = tools.float_round(
                    price, precision_rounding=rule.price_round)
            if rule.price_surcharge:
                price_surcharge = convert_to_price_uom(rule.price_surcharge)
                price += price_surcharge
            if rule.price_min_margin:
                price_min_margin = convert_to_price_uom(rule.price_min_margin)
                price = max(price, price_limit + price_min_margin)
            if rule.price_max_margin:
                price_max_margin = convert_to_price_uom(rule.price_max_margin)
                price = min(price, price_limit + price_max_margin)
        return price

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False,
                      company=False):
        if price_type == 'supplierinfo':
            prices = dict.fromkeys(self.ids, 0.0)
            for product in self:
                # Dummy price to avoid error on new pricelist base
                prices[product.id] = 1.0
            return prices
        else:
            return super(ProductProduct, self).price_compute(
                price_type, uom=uom, currency=currency, company=company)
