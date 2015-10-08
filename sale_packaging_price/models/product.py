# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    list_price = fields.Float(
        string='Package Price',
        digits_compute=dp.get_precision('Product Price'),
        help="This price will be considered as a price for complete package")
