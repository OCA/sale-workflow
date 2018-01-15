# -*- coding: utf-8 -*-
# © 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    compute_price = fields.Selection(selection_add=[('index', 'Index')])
    index_pricelist_id = fields.Many2one(
        'product.pricelist', string='Index',
        compute=lambda self: [
            this.update({'index_pricelist_id': this.base_pricelist_id})
            for this in self
        ],
        inverse=lambda self: [
            this.update({'base_pricelist_id': this.index_pricelist_id})
            for this in self
        ],
        domain=[('is_index', '=', True)],
    )
    index_price = fields.Float(
        string='Index',
        compute=lambda self: [
            this.update({'index_price': 100 - this.percent_price})
            for this in self
        ],
        inverse=lambda self: [
            this.update({'percent_price': 100 - this.index_price})
            for this in self
        ],
    )

    @api.model
    def create(self, vals):
        self._adjust_compute_price_index(vals)
        return super(ProductPricelistItem, self).create(vals)

    @api.multi
    def write(self, vals):
        self._adjust_compute_price_index(vals)
        return super(ProductPricelistItem, self).write(vals)

    # pylint: disable=api-one-deprecated
    @api.one
    @api.depends(
        'categ_id', 'product_tmpl_id', 'product_id', 'compute_price',
        'fixed_price', 'pricelist_id', 'percent_price', 'price_discount',
        'price_surcharge', 'index_pricelist_id')
    def _get_pricelist_item_name_price(self):
        super(ProductPricelistItem, self)._get_pricelist_item_name_price()
        if self.compute_price == 'index':
            self.price = _("Index %s") % self.index_pricelist_id.display_name

    def _adjust_compute_price_index(self, vals):
        if vals.get('compute_price') == 'index':
            vals.update(
                base='pricelist',
                price_discount=0,
                price_surcharge=0,
                price_min_margin=0,
                price_max_margin=0,
            )
