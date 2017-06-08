# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price_tax = fields.Float(
        string='Sale price with taxes',
        digits=dp.get_precision('Product Price'),
    )

    def _get_factor_tax(self, taxes):
        if not taxes:
            return 1.0
        if not isinstance(taxes, models.BaseModel):
            taxes = self.env['account.tax'].browse(taxes[0][2])
        tax_percent = sum(
            [tax.amount for tax in taxes if not tax.price_include])
        factor_tax = (1 + tax_percent / 100) or 1.0
        return factor_tax

    @api.model
    def create(self, vals):
        list_price_tax = vals.get('list_price_tax', 0.0)
        list_price = vals.get('list_price', 0.0)
        taxes_id = vals.get('taxes_id', False)
        if list_price_tax != 0.0:
            amount_tax = list_price_tax - (
                list_price_tax / self._get_factor_tax(taxes_id))
            vals['list_price'] = list_price_tax - amount_tax
        else:
            vals['list_price_tax'] = list_price * (
                self._get_factor_tax(taxes_id))
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        for product in self:
            if 'list_price_tax' in vals:
                taxes_id = vals.get('taxes_id', False)
                list_price_tax = vals.get('list_price_tax', 0.0)
                factor_tax = product._get_factor_tax(
                    taxes_id or product.taxes_id)
                amount_tax = list_price_tax - (list_price_tax / factor_tax)
                vals['list_price'] = list_price_tax - amount_tax
            elif 'list_price' in vals:
                taxes_id = vals.get('taxes_id', False)
                vals['list_price_tax'] = \
                    vals['list_price'] * product._get_factor_tax(
                        taxes_id or product.taxes_id)
        return super(ProductTemplate, self).write(vals)
