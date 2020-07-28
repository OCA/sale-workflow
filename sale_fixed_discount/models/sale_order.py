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
    def _onchange_discount2(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('discount_fixed')
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty',
                  'tax_id')
    def _onchange_discount(self):
        res = super(SaleOrderLine, self)._onchange_discount()

        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return res

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )
        product_context = dict(self.env.context,
                               partner_id=self.order_id.partner_id.id,
                               date=self.order_id.date_order,
                               uom=self.product_uom.id)

        price, rule_id = self.order_id \
            .pricelist_id \
            .with_context(product_context) \
            .get_product_price_rule(self.product_id,
                                    self.product_uom_qty or 1.0,
                                    self.order_id.partner_id)

        rule = self.env['product.pricelist.item'].browse(rule_id)
        if rule.compute_price == 'fixed':
            new_list_price, currency_id = self.with_context(
                product_context
            )._get_real_price_currency(product,
                                       rule_id, self.product_uom_qty,
                                       self.product_uom,
                                       self.order_id.pricelist_id.id)
            if new_list_price != 0:
                if self.order_id.pricelist_id.currency_id.id != currency_id:
                    # we need new_list_price in the same currency as price,
                    # which is in the SO's pricelist's currency
                    new_list_price = self.env['res.currency'].browse(
                        currency_id
                    ).with_context(product_context).compute(
                        new_list_price, self.order_id.pricelist_id.currency_id)
                discount = new_list_price - price
                if discount > 0:
                    self.discount_fixed = discount
                    self.discount = 0.0
        return res

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
