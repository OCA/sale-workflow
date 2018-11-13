# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class ProductLstPriceHistory(models.Model):
    "Keep track of the ``product.product`` lst prices as they are changed."
    _name = 'product.lst.price.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    company_id = fields.Many2one(
        'res.company', string='Company', default=_get_default_company_id,
        required=True)
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete='cascade', required=True)
    datetime = fields.Datetime('Date', default=fields.Datetime.now)
    lst_price = fields.Float(
        'Sale Price', digits=dp.get_precision('Product Price'))
