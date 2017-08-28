# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductSetAd(models.TransientModel):
    _name = 'product.set.add'
    _rec_name = 'product_set_id'
    _description = "Wizard model to add product set into a quotation"

    product_set_id = fields.Many2one(
        'product.set', 'Product set', required=True)
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        default=1)

    @api.multi
    def add_set(self):
        """ Add product set, multiplied by quantity in sale order line """
        so_id = self._context['active_id']
        if not so_id:
            return
        so = self.env['sale.order'].browse(so_id)
        max_sequence = 0
        if so.order_line:
            max_sequence = max([line.sequence for line in so.order_line])
        sale_order_line = self.env['sale.order.line']
        for set_line in self.product_set_id.set_line_ids:
            sale_order_line.create(
                self.prepare_sale_order_line_data(
                    so_id, self.product_set_id, set_line,
                    max_sequence=max_sequence))

    def prepare_sale_order_line_data(self, sale_order_id, set, set_line,
                                     max_sequence=0):
        sale_line = self.env['sale.order.line'].new({
            'order_id': sale_order_id,
            'product_id': set_line.product_id.id,
            'product_uom_qty': set_line.quantity * self.quantity,
            'product_uom': set_line.product_id.uom_id.id,
            'sequence': max_sequence + set_line.sequence,
        })
        sale_line.product_id_change()
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values
