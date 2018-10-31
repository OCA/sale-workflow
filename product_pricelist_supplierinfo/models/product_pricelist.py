# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False,
                            uom_id=False):
        """Recompute price after calling the atomic super method for
        getting proper prices when based on supplier info.
        """
        rule_obj = self.env['product.pricelist.item']
        result = super(ProductPricelist, self)._compute_price_rule(
            products_qty_partner, date, uom_id)
        for product, qty, _partner in products_qty_partner:
            rule = rule_obj.browse(result[product.id][1])
            if rule.base == 'supplierinfo':
                result[product.id] = (
                    product._get_price_from_supplierinfo(
                        rule, date=date, quantity=qty,
                    ), rule.id,
                )
        return result


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection(
        selection_add=[
            ('supplierinfo', 'Prices based on supplier info'),
        ],
    )
    no_supplierinfo_min_quantity = fields.Boolean(
        string='Ignore Supplier Info Min. Quantity',
    )
