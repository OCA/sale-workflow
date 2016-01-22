# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _
from openerp.osv import fields as old_fields
from openerp.exceptions import Warning
import math


class product_product(models.Model):
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

    def _product_available(
            self, cr, uid, ids, field_names=None, arg=False, context=None):
        """
        For product packs we get availability in a different way
        """
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
                'qty_available': (
                    pack_qty_available and min(pack_qty_available) or False),
                'incoming_qty': 0,
                'outgoing_qty': 0,
                'virtual_available': (
                    pack_virtual_available and
                    max(min(pack_virtual_available), 0) or False),
            }
        return res

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        """
        We use original search function
        """
        return super(product_product, self)._search_product_quantity(
            cr, uid, obj, name, domain, context)

    # overwrite ot this fields so that we can modify _product_available
    # function to support packs
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
    @api.constrains('pack_line_ids')
    def check_recursion(self):
        """
        Check recursion on packs
        """
        pack_lines = self.pack_line_ids
        while pack_lines:
            print 'pack_lines', pack_lines
            if self in pack_lines.mapped('product_id'):
                raise Warning(_(
                    'Error! You cannot create recursive packs.\n'
                    'Product id: %s') % self.id)
            pack_lines = pack_lines.mapped('product_id.pack_line_ids')


class product_template(models.Model):
    _inherit = 'product.template'

    # TODO rename a pack_type
    pack_price_type = fields.Selection([
        ('components_price', 'Detailed - Components Prices'),
        ('totalice_price', 'Detailed - Totaliced Price'),
        ('fixed_price', 'Detailed - Fixed Price'),
        ('none_detailed_assited_price', 'None Detailed - Assisted Price'),
        ('none_detailed_totaliced_price', 'None Detailed - Totaliced Price'),
    ],
        'Pack Type',
        help="""
        * Detailed - Components Prices: Detail lines with prices on sales order.
        * Detailed - Totaliced Price: Detail lines on sales order totalicing lines prices on pack (don't show component prices).
        * Detailed - Fixed Price: Detail lines on sales order and use product pack price (ignore line prices).
        * None Detailed - Assisted Price: Do not detail lines on sales order. Assist to get pack price using pack lines.
        """
        )
    pack = fields.Boolean(
        'Pack?',
        help='Is a Product Pack?',
        )
    pack_line_ids = fields.One2many(
        related='product_variant_ids.pack_line_ids'
        )
    used_pack_line_ids = fields.One2many(
        related='product_variant_ids.used_pack_line_ids'
        )

    @api.constrains(
        'parent_product_id', 'product_variant_ids', 'pack_price_type', 'pack')
    def check_relations(self):
        """
        Check assited packs dont have packs a childs
        """
        # check assited price has no packs child of them
        if self.pack_price_type == 'none_detailed_assited_price':
            child_packs = self.mapped(
                'pack_line_ids.product_id').filtered('pack')
            if child_packs:
                raise Warning(_(
                    'A "None Detailed - Assisted Price Pack" can not have a '
                    'pack as a child!'))

        # TODO we also should check this
        # check if we are configuring a pack for a product that is partof a
        # assited pack
        # if self.pack:
        #     for product in self.product_variant_ids
        #     parent_assited_packs = self.env['product.pack.line'].search([
        #         ('product_id', '=', self.id),
        #         ('parent_product_id.pack_price_type', '=',
        #             'none_detailed_assited_price'),
        #         ])
        #     print 'parent_assited_packs', parent_assited_packs
        #     if parent_assited_packs:
        #         raise Warning(_(
        #             'You can not set this product as pack because it is part '
        #             'of a "None Detailed - Assisted Price Pack"'))

    @api.one
    @api.constrains('company_id', 'product_variant_ids', 'used_pack_line_ids')
    def check_pack_line_company(self):
        """
        Check packs are related to packs of same company
        """
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

    @api.multi
    def write(self, vals):
        """
        We remove from prod.prod to avoid error
        """
        if vals.get('pack_line_ids', False):
            self.product_variant_ids.write(
                {'pack_line_ids': vals.pop('pack_line_ids')})
        return super(product_template, self).write(vals)

    @api.model
    def _price_get(self, products, ptype='list_price'):
        res = super(product_template, self)._price_get(
            products, ptype=ptype)
        for product in products:
            if (
                    product.pack and
                    product.pack_price_type in [
                        'totalice_price',
                        'none_detailed_assited_price',
                        'none_detailed_totaliced_price']):
                pack_price = 0.0
                for pack_line in product.pack_line_ids:
                    product_line_price = pack_line.product_id.price_get()[
                            pack_line.product_id.id]
                    pack_price += (product_line_price * pack_line.quantity)
                res[product.id] = pack_price
        return res
