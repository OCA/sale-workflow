##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import math


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pack_line_ids = fields.One2many(
        'product.pack.line',
        'parent_product_id',
        'Pack Products',
        help='List of products that are part of this pack.'
    )
    used_pack_line_ids = fields.One2many(
        'product.pack.line',
        'product_id',
        'On Packs',
        help='List of packs where product is used.'
    )

    def _compute_quantities_dict(
            self, lot_id, owner_id, package_id,
            from_date=False, to_date=False):
        res = super(ProductProduct, self)._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date)
        packs = self.filtered('pack')
        for product in packs.with_context(prefetch_fields=False):
            pack_qty_available = []
            pack_virtual_available = []
            for subproduct in product.pack_line_ids:
                subproduct_stock = subproduct.product_id
                sub_qty = subproduct.quantity
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock.qty_available / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock.virtual_available / sub_qty))
            # TODO calcular correctamente pack virtual available para negativos
            res[product.id] = {
                'qty_available': (
                    pack_qty_available and min(pack_qty_available) or False),
                'incoming_qty': 0,
                'outgoing_qty': 0,
                'virtual_available': (
                    pack_virtual_available and
                    max(min(pack_virtual_available), 0) or False),
            }
        return res

    @api.constrains('pack_line_ids')
    def check_recursion(self):
        """
        Check recursion on packs
        """
        for rec in self:
            pack_lines = rec.pack_line_ids
            while pack_lines:
                if rec in pack_lines.mapped('product_id'):
                    raise ValidationError(_(
                        'Error! You cannot create recursive packs.\n'
                        'Product id: %s') % rec.id)
                pack_lines = pack_lines.mapped('product_id.pack_line_ids')

    @api.multi
    def separete_pack_products(self):
        """ Divide the products and the pack products into two separate
        recordsets.
        :return: [packs, no_packs]
        """
        packs = self.filtered(lambda p: p.pack and p.pack_price_type in [
            'totalice_price',
            'none_detailed_assited_price',
            'none_detailed_totaliced_price',
        ])

        # for compatibility with website_sale
        if self._context.get('website_id', False) and \
           not self._context.get('from_cart', False):
            packs |= self.filtered(
                lambda p: p.pack and p.pack_price_type == 'components_price')

        no_packs = (self | self.mapped('pack_line_ids.product_id')) - packs
        return packs, no_packs

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False,
                      company=False):
        packs, no_packs = self.separete_pack_products()
        prices = super(ProductProduct, no_packs).price_compute(
            price_type, uom, currency, company)
        for product in packs.with_context(prefetch_fields=False):
            pack_price = 0.0
            for pack_line in product.pack_line_ids:
                product_line_price = pack_line.product_id.price * (
                    1 - (pack_line.discount or 0.0) / 100.0)
                pack_price += (product_line_price * pack_line.quantity)
            prices[product.id] = pack_price
        return prices

    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        packs, no_packs = self.separete_pack_products()
        super(ProductProduct, no_packs)._compute_product_lst_price()

        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['product.uom'].browse([self._context['uom']])
        for product in packs:
            list_price = product.price_compute('list_price').get(product.id)
            if to_uom:
                list_price = product.uom_id._compute_price(
                    list_price, to_uom)
            product.lst_price = list_price + product.price_extra
