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

    @api.multi
    def get_sale_order_line_vals(self, line, order, sequence, fiscal_position):
        self.ensure_one()
        sequence += 1
        # pack_price = 0.0
        subproduct = self.product_id
        quantity = self.quantity * line.product_uom_qty

        tax_ids = self.env['account.fiscal.position'].map_tax(
            subproduct.taxes_id)
        tax_id = [(6, 0, tax_ids)]

        if subproduct.uos_id:
            uos_id = subproduct.uos_id.id
            uos_qty = quantity * subproduct.uos_coeff
        else:
            uos_id = False
            uos_qty = quantity

        if line.product_id.pack_price_type == 'fixed_price':
            price = 0.0
            discount = 0.0
        # TODO this should go in price get of pricelist 
        # elif line.product_id.pack_price_type == 'totalice_price':
        #     pack_price += (price * uos_qty)
        #     price = 0.0
        #     discount = 0.0
        #     tax_id = False
        else:
            pricelist = order.pricelist_id.id
            price = self.env['product.pricelist'].price_get(
                subproduct.id, quantity,
                order.partner_id.id, context={
                    'uom': subproduct.uom_id.id,
                    'date': order.date_order})[pricelist]
            discount = line.discount

        # Obtain product name in partner's language
        # ctx = {'lang': order.partner_id.lang}
        subproduct_name = subproduct.name

        vals = {
            'order_id': order.id,
            'name': '%s%s' % (
                '> ' * (line.pack_depth + 1), subproduct_name
            ),
            'sequence': sequence,
            # 'delay': subproduct.sale_delay or 0.0,
            'product_id': subproduct.id,
            # 'procurement_ids': (
            #     [(4, x.id) for x in line.procurement_ids]
            # ),
            'price_unit': price,
            'tax_id': tax_id,
            'address_allotment_id': False,
            'product_uom_qty': quantity,
            'product_uom': subproduct.uom_id.id,
            'product_uos_qty': uos_qty,
            'product_uos': uos_id,
            'product_packaging': False,
            'discount': discount,
            'number_packages': False,
            'th_weight': False,
            'state': 'draft',
            'pack_parent_line_id': line.id,
            'pack_depth': line.pack_depth + 1,
        }
        return vals


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
