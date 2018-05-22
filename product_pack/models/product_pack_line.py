##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class ProductPack(models.Model):
    _name = 'product.pack.line'
    _rec_name = 'product_id'

    parent_product_id = fields.Many2one(
        'product.product',
        'Parent Product',
        ondelete='cascade',
        index=True,
        required=True
    )
    quantity = fields.Float(
        required=True,
        default=1.0,
        digits=dp.get_precision('Product UoS'),
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        ondelete='cascade',
        index=True,
        required=True,
    )
    discount = fields.Float(
        'Discount (%)',
        digits=dp.get_precision('Discount'),
    )

    @api.multi
    def get_sale_order_line_vals(self, line, order):
        self.ensure_one()
        # pack_price = 0.0
        subproduct = self.product_id
        quantity = self.quantity * line.product_uom_qty

        taxes = order.fiscal_position_id.map_tax(
            subproduct.taxes_id.filtered(
                lambda r: r.company_id.id == order.company_id.id))
        tax_id = [(6, 0, taxes.ids)]

        # if pack is fixed price or totlice price we don want amount on
        # pack lines
        if line.product_id.pack_price_type in [
                'fixed_price', 'totalice_price']:
            price = 0.0
            discount = 0.0
        else:
            pricelist = order.pricelist_id.id
            price = self.env['product.pricelist'].with_context(
                context={
                    'uom': subproduct.uom_id.id,
                    'date': order.date_order,
                }
            ).price_get(
                subproduct.id, quantity,
                order.partner_id.id)[pricelist]
            discount = self.discount

        # Obtain product name in partner's language
        if order.partner_id.lang:
            subproduct = subproduct.with_context(
                lang=order.partner_id.lang)
        subproduct_name = subproduct.name

        vals = {
            'order_id': order.id,
            'name': '%s%s' % (
                '> ' * (line.pack_depth + 1), subproduct_name
            ),
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
            'product_packaging': False,
            'discount': discount,
            'number_packages': False,
            'th_weight': False,
            'state': 'draft',
            'pack_parent_line_id': line.id,
            'pack_depth': line.pack_depth + 1,
        }
        return vals
