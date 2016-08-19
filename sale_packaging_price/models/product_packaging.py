# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl

from openerp import _, api, fields, models
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductPackagingMaterial(models.Model):
    _name = 'product.packaging.material'

    name = fields.Char(string='Package Material')


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    list_price = fields.Float(
        string='Package Price',
        digits_compute=dp.get_precision('Product Price'),
        help="This price will be considered as a price for complete package")
    package_material_id = fields.Many2one(
        comodel_name='product.packaging.material',
        string='Package Material')
    weight = fields.Float(
        string='Package Weight',
        digits_compute=dp.get_precision('Stock Weight'),
        help="Weight of the package itself, wighout counting inner products.")

    @api.onchange('list_price', 'qty')
    def _onchange_list_price(self):
        price_precision = self.env['decimal.precision'].precision_get(
            'Product Price')
        if self.qty:
            price_computed = (
                round(self.list_price / self.qty, price_precision) *
                self.qty)
        else:
            price_computed = 0.0
        if str(self.list_price) != str(price_computed):
            return {
                'warning': {
                    'title': _('Problem with price'),
                    'message': _(
                        "With the current decimal precision, you can't get "
                        "this price. (Approx. price suggested: %s)"
                    ) % str(price_computed)
                }
            }
