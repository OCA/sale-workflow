# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        vals = {}
        for line in self.mapped('order_line').filtered(
                lambda l: l.discount_fixed):
            vals[line] = {
                'price_unit': line.price_unit,
                'discount_fixed': line.discount_fixed,
            }
            price_unit = line.price_unit - line.discount_fixed
            line.update({
                'price_unit': price_unit,
                'discount_fixed': 0.0,
            })
        res = super(SaleOrder, self)._amount_all()
        for line in vals.keys():
            line.update(vals[line])
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits=dp.get_precision('Product Price'),
        help="Fixed amount discount.")

    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('discount_fixed')
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.constrains('discount', 'discount_fixed')
    def _check_only_one_discount(self):
        for line in self:
            if line.discount and line.discount_fixed:
                raise ValidationError(
                    _("You can only set one type of discount per line."))

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id',
                 'discount_fixed')
    def _compute_amount(self):
        vals = {}
        for line in self.filtered(lambda l: l.discount_fixed):
            vals[line] = {
                'price_unit': line.price_unit,
                'discount_fixed': line.discount_fixed,
            }
            price_unit = line.price_unit - line.discount_fixed
            line.update({
                'price_unit': price_unit,
                'discount_fixed': 0.0,
            })
        res = super(SaleOrderLine, self)._compute_amount()
        for line in vals.keys():
            line.update(vals[line])
        return res

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount_fixed': self.discount_fixed,
        })
        return res
