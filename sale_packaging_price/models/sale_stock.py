# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import math

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    packaging_price = fields.Float(
        related='product_packaging.list_price', string='Package Price',
        readonly=True)
    product_packaging = fields.Many2one(ondelete='restrict')
    packaging_weight = fields.Float(
        string='Package Weight',
        digits_compute=dp.get_precision('Stock Weight'))

    @api.multi
    def product_packaging_change(
            self, pricelist, product, qty=0, uom=False, partner_id=False,
            packaging=False, flag=False):
        res = super(SaleOrderLine, self).product_packaging_change(
            pricelist, product, qty, uom, partner_id, packaging, flag)
        if packaging:
            product_packaging = self.env['product.packaging'].browse(packaging)
            product_prec = self.env['decimal.precision'].precision_get(
                'Product Price')
            res['value']['price_unit'] = round(
                product_packaging.list_price / product_packaging.qty,
                product_prec)
            package_weight = math.ceil(
                qty / product_packaging.qty) * product_packaging.ul.weight
            res['value']['packaging_weight'] = package_weight
        else:
            res = self.product_id_change(
                pricelist=pricelist, product=product, qty=qty, uom=uom,
                partner_id=partner_id, packaging=packaging, flag=False)
            price_unit = res['value'].get('price_unit', 0.0)
            package_weight = res['value'].get('packaging_weight', 0.0)
            res['value'] = {'price_unit': price_unit,
                            'packaging_weight': package_weight}
        return res
