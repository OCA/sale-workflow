# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductSet(models.Model):
    _name = 'product.set'
    _description = 'Product set'

    name = fields.Char(help='Product set name', required=True)
    ref = fields.Char(
        string='Internal Reference',
        help='Product set internal reference',
        copy=False,
    )
    set_line_ids = fields.One2many(
        'product.set.line', 'product_set_id', string="Products"
    )

    @api.multi
    def name_get(self):
        return [
            (
                product_set.id,
                '%s%s'
                % (
                    product_set.ref and '[%s] ' % product_set.ref or '',
                    product_set.name,
                ),
            )
            for product_set in self
        ]
