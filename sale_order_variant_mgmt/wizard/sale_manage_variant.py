# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.addons.decimal_precision as dp
from openerp import api, models, fields


class SaleManageVariant(models.TransientModel):
    _name = 'sale.manage.variant'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string="Template", required=True)
    variant_line_ids = fields.Many2many(
        comodel_name='sale.manage.variant.line', string="Variant Lines")

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.variant_line_ids = [(6, 0, [])]
        template = self.product_tmpl_id
        if template and len(template.attribute_line_ids) >= 2:
            line_x = template.attribute_line_ids[0]
            line_y = template.attribute_line_ids[1]
            lines = []
            for value_x in line_x.value_ids:
                for value_y in line_y.value_ids:
                    # Filter the corresponding product for that values
                    product = template.product_variant_ids.filtered(
                        lambda x: (value_x in x.attribute_value_ids and
                                   value_y in x.attribute_value_ids))
                    lines.append((0, 0, {
                        'product_id': product,
                        'disabled': not bool(product),
                        'value_x': value_x,
                        'value_x_label': value_x.name,
                        'value_y': value_y,
                        'value_y_label': value_y.name,
                        'product_uom_qty': 0,
                    }))
            self.variant_line_ids = lines

    @api.multi
    def button_transfer_to_order(self):
        context = self.env.context
        sale_order = self.env['sale.order'].browse(context.get('active_id'))
        OrderLine = self.env['sale.order.line']
        for line in self.variant_line_ids:
            order_line = sale_order.order_line.filtered(
                lambda x: x.product_id == line.product_id)
            if order_line:
                if not line.product_uom_qty:
                    order_line.unlink()
                else:
                    order_line.product_uom_qty = line.product_uom_qty
            elif line.product_uom_qty:
                order_line = OrderLine.new({
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'order_id': sale_order.id,
                })
                order_line.product_id_change()
                order_line_vals = order_line.convert_to_write(
                    order_line._cache)
                sale_order.order_line.create(order_line_vals)


class SaleManageVariantLine(models.TransientModel):
    _name = 'sale.manage.variant.line'

    product_id = fields.Many2one(
        comodel_name='product.product', string="Variant", readonly=True)
    disabled = fields.Boolean()
    value_x = fields.Many2one(comodel_name='product.attribute.value')
    value_y = fields.Many2one(comodel_name='product.attribute.value')
    # Direct values as labels are not got from many2one fields and related
    # fields are also not computed when drawing the widget
    value_x_label = fields.Char()
    value_y_label = fields.Char()
    product_uom_qty = fields.Float(
        string="Quantity", digits_compute=dp.get_precision('Product UoS'))
