# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains('order_line')
    def check_constraint_min_qty(self):
        for order in self:
            invaild_lines = []
            line_to_test = order.order_line.filtered(
                lambda l: not l.product_id.force_sale_min_qty and
                l.product_uom_qty < l.product_id.sale_min_qty)
            for line in line_to_test:
                invaild_lines.append(_('Product "%s": Min Quantity %s.') % (line.product_id.name, line.product_id.sale_min_qty)) 

            if invaild_lines:
                msg = _('Check minimum order quantity for this products: * \n') +\
                        '\n '.join(invaild_lines)
                msg += _('\n* If you want sell quantity less then Min Quantity'
                        ',Check "force min quatity" on product')
                raise ValidationError(msg)  


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_min_qty = fields.Float(string='Min Qty',
            related='product_id.sale_min_qty', readonly=True, store=True)
    force_sale_min_qty = fields.Boolean(
            related='product_id.force_sale_min_qty', readonly=True, store=True)
    is_qty_less_min_qty = fields.Boolean(string='Qty < Min Qty', compute='_get_is_qty_less_min_qty',)


    @api.multi
    @api.depends('product_uom_qty', 'sale_min_qty')
    def _get_is_qty_less_min_qty(self):
        for line in self:
            line.is_qty_less_min_qty = line.product_uom_qty < line.sale_min_qty

