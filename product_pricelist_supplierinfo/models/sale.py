# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_real_price_currency(self, product, rule_id, qty, uom,
                                 pricelist_id):
        price, currency = super(SaleOrderLine, self)._get_real_price_currency(
            product, rule_id, qty, uom, pricelist_id)
        item_obj = self.env['product.pricelist.item']
        product_currency = None
        if rule_id:
            pricelist_item = item_obj.browse(rule_id)
            if pricelist_item.base == 'supplierinfo':
                currency_id = pricelist_item.pricelist_id.currency_id
                product_currency = product_currency or (
                    product.company_id and
                    product.company_id.currency_id) or \
                    self.env.user.company_id.currency_id
                if not currency_id:
                    currency_id = product_currency
                    cur_factor = 1.0
                else:
                    if currency_id.id == product_currency.id:
                        cur_factor = 1.0
                    else:
                        cur_factor = currency_id._get_conversion_rate(
                            product_currency, currency_id)
                product_uom = self.env.context.get('uom') or product.uom_id.id
                if uom and uom.id != product_uom:
                    # the unit price is in a different uom
                    uom_factor = uom._compute_price(1.0, product.uom_id)
                else:
                    uom_factor = 1.0
                price = product.get_price_from_supplierinfo(pricelist_item)
                return price * uom_factor * cur_factor, currency_id.id
        return price, currency
