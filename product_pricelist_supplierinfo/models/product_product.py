# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, tools


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_price_from_supplierinfo(self, rule, date=None, quantity=None):
        """Method for getting the price from supplier info."""
        self.ensure_one()
        domain = [('id', 'in', self.seller_ids.ids)]
        if not rule.no_supplierinfo_min_quantity and quantity:
            domain += [
                '|',
                ('min_qty', '=', False),
                ('min_qty', '>=', quantity),
            ]
        if date:
            domain += [
                '|',
                ('date_start', '=', False),
                ('date_start', '<=', date),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', date),
            ]
        # We use a different default order because we are interested in getting
        # the price for lowest minimum quantity
        price = self.env['product.supplierinfo'].search(
            domain, limit=1, order='sequence, min_qty, price',
        )[-1:].price
        if price:
            # We have to replicate this logic in this method as pricelist
            # method are atomic and we can't hack inside.
            # Verbatim copy of part of product.pricelist._compute_price_rule.
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
        """Return dummy not falsy prices when computation is done from supplier
        info for avoiding error on super method. We will later fill these with
        correct values.
        """
        if price_type == 'supplierinfo':
            return dict.fromkeys(self.ids, 1.0)
        return super(ProductProduct, self).price_compute(
            price_type, uom=uom, currency=currency, company=company)
