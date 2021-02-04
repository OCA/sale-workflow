# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import partial

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits=dp.get_precision('Product Price'),
        help="Fixed amount discount.")

    @api.onchange('discount')
    def _onchange_discount_percent(self):
        # _onchange_discount method already exists in core,
        # but discount is not in the onchange definition
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
            real_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0
                                            ) - (line.discount_fixed or 0.0)
            twicked_price = real_price / (1 - (line.discount or 0.0) / 100.0)
            vals[line] = {
                'price_unit': line.price_unit,
            }
            line.update({
                'price_unit': twicked_price,
            })
        res = super(SaleOrderLine, self)._compute_amount()
        for line in vals.keys():
            line.update(vals[line])
        return res

    @api.depends('price_unit', 'discount', 'discount_fixed')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0) - (line.discount_fixed or 0.0)

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount_fixed': self.discount_fixed,
        })
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                taxes = line.tax_id.compute_all(line.price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]