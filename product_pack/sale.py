# -*- encoding: latin-1 -*-
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class sale_order_line_pack_line(models.Model):
    _name = 'sale.order.line.pack.line'
    _description = 'sale.order.line.pack.line'

    order_line_id = fields.Many2one(
        'sale.order.line', 'Order Line', ondelete='cascade', required=True)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits_compute=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(
        compute="_amount_line",
        string='Subtotal',
        digits_compute=dp.get_precision('Account'))
    product_uom_qty = fields.Float(
        'Quantity', digits_compute=dp.get_precision('Product UoS'),
        required=True)
    # product_uom = fields.Many2one(
    #     'product.uom', 'Unit of Measure ', required=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_unit = self.product_id.lst_price

    @api.one
    @api.depends('price_unit', 'product_uom_qty')
    def _amount_line(self):
        self.price_subtotal = self.product_uom_qty * self.price_unit


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    pack_total = fields.Float(
        string='Pack total', compute='_get_pack_total')
    pack_line_ids = fields.One2many(
        'sale.order.line.pack.line', 'order_line_id', 'Pack Lines')

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    @api.one
    @api.depends(
        'pack_line_ids',
        'pack_line_ids.price_subtotal',
        )
    def _get_pack_total(self):
        pack_total = 0.0
        if self.pack_line_ids:
            pack_total = sum(x.price_subtotal for x in self.pack_line_ids)
        self.pack_total = pack_total

    @api.one
    @api.onchange('pack_total')
    def _onchange_pack_line_ids(self):
        self.price_unit = self.pack_total

    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        # warning = {}
        if not product:
            return {'value': {
                'th_weight': 0,
                'product_packaging': False,
                'product_uos_qty': qty},
                'domain': {'product_uom': [], 'product_uos': []}
                }
        product_obj = self.pool.get('product.product')
        product_info = product_obj.browse(cr, uid, product)

        result = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging,
            fiscal_position, flag, context)

        pack_line_ids = [(5, False, False)]
        if product_info.pack_line_ids:
            for pack_line in product_info.pack_line_ids:
                price_unit = pack_line.product_id.lst_price
                quantity = pack_line.quantity
                pack_line_ids.append((0, False, {
                    'product_id': pack_line.product_id.id,
                    'product_uom_qty': quantity,
                    'price_unit': price_unit,
                    'price_subtotal': price_unit * quantity,
                    }))
        result['value']['pack_line_ids'] = pack_line_ids
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
