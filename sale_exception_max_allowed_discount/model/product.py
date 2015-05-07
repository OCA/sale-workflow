# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_max_sale_discount = fields.Boolean(
        'Applicable Maximum Discount',
        default=False)
    max_sale_discount = fields.Float(
        'Maximum Discount (%)', digits_compute=dp.get_precision('Discount'),
        help="Maximum sales discount defined for this product. Sales "
             "quotations containing products where the discount of the "
             "line exceeds the discount defined in the product will be "
             "blocked.")

    _sql_constraints = [
        ('max_sale_discount_max_limit', 'CHECK (max_sale_discount <= 100.0)',
         _('Maximum discount must be lower than 100%.')),
        ('max_sale_discount_min_limit', 'CHECK (max_sale_discount >= 0.0)',
         _('Maximum discount must be higher than 0%.')),
    ]

    @api.one
    @api.onchange('has_max_sale_discount')
    def onchange_has_max_sale_discount(self):
        if not self.has_max_sale_discount:
            self.max_sale_discount = 0.0

    @api.one
    @api.onchange('max_sale_discount')
    def onchange_max_sale_discount(self):
        self.has_max_sale_discount = bool(self.max_sale_discount)


class Product(models.Model):
    _inherit = "product.product"

    @api.one
    @api.onchange('has_max_sale_discount')
    def onchange_has_max_sale_discount(self):
        if not self.has_max_sale_discount:
            self.max_sale_discount = 0.0

    @api.one
    @api.onchange('max_sale_discount')
    def onchange_max_sale_discount(self):
        self.has_max_sale_discount = bool(self.max_sale_discount)