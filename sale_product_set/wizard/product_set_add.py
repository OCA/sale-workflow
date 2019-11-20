# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp


class ProductSetAdd(models.TransientModel):
    _name = 'product.set.add'
    _rec_name = 'product_set_id'
    _description = "Wizard model to add product set into a quotation"

    order_id = fields.Many2one(
        'sale.order', 'Sale Order', required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    partner_id = fields.Many2one(related='order_id.partner_id')
    product_set_id = fields.Many2one(
        'product.set', 'Product set', required=True)
    quantity = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        default=1)
    skip_existing_products = fields.Boolean(
        default=False,
        help='Enable this to not add new lines '
        'for products already included in SO lines.'
    )

    def _check_partner(self):
        if self.product_set_id.partner_id:
            if self.product_set_id.partner_id != self.order_id.partner_id:
                raise exceptions.ValidationError(_(
                    "Select a product set assigned to "
                    "the same partner of the order."
                ))

    @api.multi
    def add_set(self):
        """ Add product set, multiplied by quantity in sale order line """
        self._check_partner()
        order_lines = self._prepare_order_lines()
        if order_lines:
            self.order_id.write({
                "order_line": order_lines
            })
        return order_lines

    def _prepare_order_lines(self):
        max_sequence = self._get_max_sequence()
        order_lines = []
        for set_line in self._get_lines():
            order_lines.append(
                (0, 0,
                 self.prepare_sale_order_line_data(
                     set_line, max_sequence=max_sequence))
            )
        return order_lines

    def _get_max_sequence(self):
        max_sequence = 0
        if self.order_id.order_line:
            max_sequence = max([
                line.sequence for line in self.order_id.order_line
            ])
        return max_sequence

    def _get_lines(self):
        # hook here to take control on used lines
        so_product_ids = self.order_id.order_line.mapped('product_id').ids
        for set_line in self.product_set_id.set_line_ids:
            if (self.skip_existing_products
                    and set_line.product_id.id in so_product_ids):
                continue
            yield set_line

    @api.multi
    def prepare_sale_order_line_data(self, set_line,
                                     max_sequence=0):
        self.ensure_one()
        sale_line = self.env['sale.order.line'].new({
            'order_id': self.order_id.id,
            'product_id': set_line.product_id.id,
            'product_uom_qty': set_line.quantity * self.quantity,
            'product_uom': set_line.product_id.uom_id.id,
            'sequence': max_sequence + set_line.sequence,
            'discount': set_line.discount,
        })
        sale_line.product_id_change()
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values
