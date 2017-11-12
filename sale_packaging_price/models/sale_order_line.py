# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    packaging_price = fields.Float(
        related='product_packaging.list_price', string='Package Price',
        readonly=True)
    product_packaging = fields.Many2one(ondelete='restrict')
    packaging_weight = fields.Float(
        string='Package Weight',
        digits=dp.get_precision('Stock Weight'))

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if self.product_packaging.qty > 0.0:
            self._check_package()
        else:
            super(SaleOrderLine, self).product_uom_change()

    @api.multi
    def _check_package(self):
        price_precision = self.env['decimal.precision'].precision_get(
            'Product Price')
        qty = self.product_id.uom_id._compute_quantity(
            self.product_packaging.qty,
            self.product_uom)

        self.price_unit = round(self.product_packaging.list_price / qty,
                                price_precision)
        self.packaging_weight = (
            qty * self.product_id.weight + self.product_packaging.weight)
        return super(SaleOrderLine, self)._check_package()
