# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False,
                            uom_id=False):
        rule_obj = self.env['product.pricelist.item']
        result = super(ProductPricelist, self)._compute_price_rule(
            products_qty_partner, date, uom_id)
        products = [item[0] for item in products_qty_partner]
        for product in products:
            price, rule_id = result[product.id]
            rule = rule_obj.browse(rule_id)
            if rule.base == 'supplierinfo':
                price = product.get_price_from_supplierinfo(rule)
                if price:
                    result[product.id] = (price, rule_id)
        return result


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection(
        selection_add=[
            ('supplierinfo', 'Prices based on supplier info'),
        ],
    )
    no_min_quantity = fields.Boolean(
        string='Ignore Min. Quantity',
    )

    @api.onchange('no_min_quantity')
    def onchange_no_min_quantity(self):
        self.min_quantity = int(self.no_min_quantity)
