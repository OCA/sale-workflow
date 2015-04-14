# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _
from openerp.osv import fields as old_fields
from openerp.exceptions import Warning
import math


class product_pack(models.Model):
    _name = 'product.pack.line'
    _rec_name = 'product_id'

    parent_product_id = fields.Many2one(
        'product.product', 'Parent Product',
        ondelete='cascade', required=True)
    quantity = fields.Float(
        'Quantity', required=True)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True)


class product_product(models.Model):
    _inherit = 'product.product'

    pack_line_ids = fields.One2many(
        'product.pack.line', 'parent_product_id', 'Pack Products',
        help='List of products that are part of this pack.')
    used_pack_line_ids = fields.One2many(
        'product.pack.line', 'product_id', 'Pack Products',
        help='List of products that are part of this pack.')

    def _product_available(
            self, cr, uid, ids, field_names=None, arg=False, context=None):
        pack_product_ids = self.search(cr, uid, [
            ('pack', '=', True),
            ('id', 'in', ids),
        ])
        res = super(product_product, self)._product_available(
            cr, uid, list(set(ids) - set(pack_product_ids)),
            field_names, arg, context)
        for product in self.browse(cr, uid, pack_product_ids, context=context):
            pack_qty_available = []
            pack_virtual_available = []
            for subproduct in product.pack_line_ids:
                subproduct_stock = self._product_available(
                    cr, uid, [subproduct.product_id.id], field_names, arg,
                    context)[subproduct.product_id.id]
                sub_qty = subproduct.quantity
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock['qty_available'] / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock['virtual_available'] / sub_qty))
            # TODO calcular correctamente pack virtual available para negativos
            res[product.id] = {
                'qty_available': pack_qty_available and min(pack_qty_available) or False,
                'incoming_qty': 0,
                'outgoing_qty': 0,
                'virtual_available': pack_virtual_available and max(min(pack_virtual_available), 0) or False,
            }
        return res

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        return super(product_product, self)._search_product_quantity(
            cr, uid, obj, name, domain, context)

    _columns = {
        'qty_available': old_fields.function(
            _product_available, multi='qty_available',
            fnct_search=_search_product_quantity),
        'virtual_available': old_fields.function(
            _product_available, multi='qty_available',
            fnct_search=_search_product_quantity),
        'incoming_qty': old_fields.function(
            _product_available, multi='qty_available',
            fnct_search=_search_product_quantity),
        'outgoing_qty': old_fields.function(
            _product_available, multi='qty_available',
            fnct_search=_search_product_quantity),
    }

    @api.one
    @api.constrains('company_id', 'pack_line_ids', 'used_pack_line_ids')
    def check_pack_line_company(self):
        # TODO implementar mejores mensajes
        for line in self.pack_line_ids:
            if line.product_id.company_id != self.company_id:
                raise Warning(_(
                    'Pack lines products company must be the same as the\
                    parent product company'))
        for line in self.used_pack_line_ids:
            if line.parent_product_id.company_id != self.company_id:
                raise Warning(_(
                    'Pack lines products company must be the same as the\
                    parent product company'))


class product_template(models.Model):
    _inherit = 'product.template'

    pack_price_type = fields.Selection([
        ('components_price', 'Components Prices'),
        # TODO modify price_get and add this functionality
        # ('totalice_price', 'Totalice Price'),
        ('fixed_price', 'Fixed Price'),
    ],
        'Pack Price Type',
        help="""
        * Totalice Price: Sum individual prices on the product pack price.
        * Fixed Price: Price of this product instead of components prrices.
        * Components Price: Components prices plast pack price.
        """
    )
    sale_order_pack = fields.Boolean(
        'Sale Order Pack',
        help='Sale order are packs used on sale orders to calculate a price of a line',
    )
    pack = fields.Boolean(
        'Pack?',
        help='TODO',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
