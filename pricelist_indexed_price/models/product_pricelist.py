# -*- coding: utf-8 -*-
# © 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_index = fields.Boolean(
        'Is index', help='If this is set, this pricelist should be edited via '
        'the index functionality')
    item_ids = fields.One2many(
        default=lambda self: self._get_default_item_ids(),
    )

    @api.model
    def _get_default_item_ids(self):
        if self.default_get(['is_index']).get('is_index'):
            return [
                [0, False, {'compute_price': 'percentage', 'index_price': 100}]
            ]
        return super(ProductPricelist, self)._get_default_item_ids()

    @api.model
    def _where_calc(self, domain, active_test=True):
        # do the same as for active test, but then with a default for is_index
        if domain and not self.default_get(['is_index']).get('is_index') and\
           all(leaf[0] != 'is_index' for leaf in domain):
            domain = [('is_index', '!=', True)] + domain
        return super(ProductPricelist, self)._where_calc(
            domain, active_test=active_test
        )
