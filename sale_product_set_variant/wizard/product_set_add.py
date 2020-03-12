# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class ProductSetAddLine(models.TransientModel):
    _name = 'product.set.add.line'
    _description = 'Product add line'
    _order = 'sequence'

    wiz_id = fields.Many2one(
        'product.set.add',
    )
    source_line_id = fields.Many2one(
        'product.set.line',
    )
    product_variant_ids = fields.Many2many(
        'product.product',
        domain="""[
            '&',
            ('sale_ok', '=', True),
            ('product_tmpl_id', '=', product_template_id),
        ]""",
        string='Products',
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
        string='Product Template',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=0,
    )

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        for record in self:
            variants = record.product_template_id.product_variant_ids
            if len(variants) == 1:
                record.product_variant_ids = [(6, 0, variants.ids)]
            else:
                record.product_variant_ids = [(5, 0, 0)]


class ProductSetAdd(models.TransientModel):
    _inherit = 'product.set.add'

    product_set_id = fields.Many2one(
        'product.set',
        'Product set',
        required=True,
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
                        "Product Template is not selected in Product Set"
                    ))
                vals.append((0, 0, self._get_wiz_line_values(line)))
        self.update({
            "set_line_ids": vals,
        })

    def _get_wiz_line_values(self, set_line):
        return {
            'source_line_id': set_line.id,
            'product_variant_ids': [
                (6, 0, set_line.product_variant_ids.ids)
            ],
            'quantity': set_line.quantity,
            'product_template_id': set_line.product_template_id.id,
            'sequence': set_line.sequence
        }

    def _prepare_order_lines(self):
        max_sequence = self._get_max_sequence()
        order_lines = []
        for set_line in self._get_lines():
            if not set_line.product_variant_ids:
                variants = set_line.product_template_id.product_variant_ids
                if len(variants) == 1:
                    set_line.product_variant_ids = [(6, 0, variants.ids)]
                else:
                    raise UserError(
                        _("Please select the "
                          "appropriate product variants "
                          "for product {}").format(
                              set_line.product_template_id.name))
            for variant in set_line.product_variant_ids:
                order_lines.append(
                    (0, 0,
                     self.prepare_sale_order_line_data(
                         set_line,
                         variant,
                         max_sequence=max_sequence
                     ))
                )
        return order_lines

    def _get_lines(self):
        # hook here to take control on used lines
        return self.set_line_ids

    def prepare_sale_order_line_data(self, set_line, variant,
                                     max_sequence=0):
        sale_line = self.env['sale.order.line'].new({
            'order_id': self.order_id.id,
            'product_id': variant.id,
            'product_uom_qty': set_line.quantity * self.quantity,
            'product_uom': variant.uom_id.id,
            'sequence': max_sequence + set_line.sequence,
        })
        sale_line.product_id_change()
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values
