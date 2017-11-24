# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class WizardProductSetLine(models.TransientModel):
    _name = 'product.set.add.line'
    _order = 'sequence'

    wiz_id = fields.Many2one(
        'product.set.add',
    )
    source_line_id = fields.Many2one(
        'product.set.line',
    )
    product_variant_ids = fields.Many2many(
        'product.product', domain=[('sale_ok', '=', True)],
        string='Product',
        required=False,
    )
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_set_id = fields.Many2one(
        'product.set',
        string='Set',
        related='source_line_id.product_set_id',
        readonly=True,
    )
    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=0,
    )


class ProductSetAd(models.TransientModel):
    _inherit = 'product.set.add'

    product_set_id = fields.Many2one(
        'product.set',
        'Product set',
        required=True
    )
    set_line_ids = fields.One2many(
        'product.set.add.line',
        'wiz_id',
        string='Products',
    )

    @api.onchange('product_set_id')
    def _onchange_product_set_id(self):
        vals = []
        if self.product_set_id:
            for line in self.product_set_id.set_line_ids:
                if not line.product_template_id:
                    raise ValidationError(_(
                        "No selected product_template_id in Product Set"
                    ))
                wiz_line_vals = {
                    'source_line_id': line.id,
                    'product_variant_ids': [
                        (6, 0, line.product_variant_ids.ids)
                    ],
                    'quantity': line.quantity,
                    'product_template_id': line.product_template_id.id,
                    'sequence': line.sequence
                }
                vals.append((0, 0, wiz_line_vals))
        self.update({
            "set_line_ids": vals,
        })

    @api.multi
    def add_set(self):
        """ Add product set, multiplied by quantity in sale order line """
        self.ensure_one()
        so_id = self.env.context.get('active_id')
        if not so_id:
            return
        so = self.env['sale.order'].browse(so_id)
        max_sequence = 0
        if so.order_line:
            max_sequence = max([line.sequence for line in so.order_line])
        so_lines = []
        for set_line in self.set_line_ids:
            if not set_line.product_variant_ids:
                raise UserError(_("Please select the "
                                  "appropriate product variants"))
            for variant in set_line.product_variant_ids:
                so_lines.append((0, 0, self.prepare_sale_order_line_data(
                    so_id, set_line, variant,
                    max_sequence=max_sequence)))
        if so_lines:
            so.write({
                "order_line": so_lines
            })

    def prepare_sale_order_line_data(self, sale_order_id, set_line, variant,
                                     max_sequence=0):
        sale_line = self.env['sale.order.line'].new({
            'order_id': sale_order_id,
            'product_id': variant.id,
            'product_uom_qty': set_line.quantity * self.quantity,
            'product_uom': variant.uom_id.id,
            'sequence': max_sequence + set_line.sequence,
        })
        sale_line.product_id_change()
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values
