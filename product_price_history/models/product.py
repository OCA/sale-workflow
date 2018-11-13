# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def view_product_price_history(self):
        return {
            'name': _('Cost Price History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.price.history',
            'type': 'ir.actions.act_window',
            'domain': [('product_id', 'in', self.product_variant_ids.ids)],
        }

    @api.multi
    def view_product_lst_price_history(self):
        return {
            'name': _('Sale Price History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.lst.price.history',
            'type': 'ir.actions.act_window',
            'domain': [('product_id', 'in', self.product_variant_ids.ids)],
        }

    @api.model
    def create(self, vals):
        product = super(ProductTemplate, self).create(vals)
        product._set_historical_lst_price()
        return product

    @api.multi
    def write(self, values):
        ''' Store the lst price change in order to be able to retrieve the
        sale price of a product for a given date'''
        res = super(ProductTemplate, self).write(values)
        if 'list_price' in values:
            self._set_historical_lst_price()
        return res

    @api.multi
    def _set_historical_lst_price(self):
        ''' Store the lst price change in order to be able to retrieve the cost
        of a product for a given date'''
        PriceHistory = self.env['product.lst.price.history']
        for product in self:
            for variant in product.product_variant_ids:
                PriceHistory.create({
                    'product_id': variant.id,
                    'lst_price': variant.lst_price,
                    'company_id': self._context.get(
                        'force_company', self.env.user.company_id.id),
                })


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def view_product_price_history(self):
        return {
            'name': _('Cost Price History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.price.history',
            'type': 'ir.actions.act_window',
            'domain': [('product_id', '=', self.id)],
        }

    def view_product_lst_price_history(self):
        return {
            'name': _('Sale Price History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.price.history',
            'type': 'ir.actions.act_window',
            'domain': [('product_id', '=', self.id)],
        }
