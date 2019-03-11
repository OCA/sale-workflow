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

    # because on expand_pack_line we are searhing for existing product, we
    # need to enforce this condition
    _sql_constraints = [
        ('product_uniq', 'unique(parent_product_id, product_id)',
         'Product must be only once on a pack!'),
    ]

    @api.multi
    def get_sale_order_line_vals(self, line, order):
        self.ensure_one()
        quantity = self.quantity * line.product_uom_qty
        line_vals = {
            'order_id': order.id,
            'product_id': self.product_id.id or False,
            'pack_parent_line_id': line.id,
            'pack_depth': line.pack_depth + 1,
            # 'sequence': sequence,
            'company_id': order.company_id.id,
        }
        sol = line.new(line_vals)
        sol.product_id_change()
        sol.product_uom_qty = quantity
        sol.product_uom_change()
        sol._onchange_discount()
        vals = sol._convert_to_write(sol._cache)

        discount = 100.0 - (
            (100.0 - sol.discount) * (100.0 - self.discount) / 100.0)

        vals.update({
            'discount': discount,
            'name': '%s%s' % (
                '> ' * (line.pack_depth + 1), sol.name
            ),
        })
        return vals
