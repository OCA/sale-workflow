# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class ProductSetAdd(models.TransientModel):
    _name = 'product.set.add'
    _rec_name = 'product_set_id'
    _description = "Wizard to add product set into a quotation"

    product_set_id = fields.Many2one(
        'product.set', string='Product set', required=True, ondelete='cascade')
    quantity = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        default=1)

    @api.multi
    def add_set(self):
        """ Add product set, multiplied by quantity in sale order """
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
            'product_uom': set_line.product_id.uom_id.id,
            'product_uom_qty': set_line.quantity * self.quantity,
            'sequence': max_sequence + set_line.sequence,
        })
        sale_line.product_id_change()
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values
