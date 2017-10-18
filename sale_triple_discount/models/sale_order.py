# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            if not order.company_id.tax_calculation_rounding_method == (
                    'round_globally'):
                return super(SaleOrder, self)._amount_all()
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                price = line.price_unit * (
                    1 - (line.discount or 0.0) / 100.0) * (
                    1 - (line.discount2 or 0.0) / 100.0) * (
                    1 - (line.discount3 or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(
                    price,
                    line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=order.partner_shipping_id,
                )
                amount_tax += sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', []))
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(
                    amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('discount2', 'discount3')
    def _compute_amount(self):
        for line in self:
            prev_price_unit = line.price_unit
            prev_discount = line.discount
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
            })
            super(SaleOrderLine, line)._compute_amount()
            line.update({
                'price_unit': prev_price_unit,
                'discount': prev_discount,
            })

    discount2 = fields.Float(
        'Disc. 2 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )
    discount3 = fields.Float(
        'Disc. 3 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Discount 2 must be lower than 100%.'),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         'Discount 3 must be lower than 100%.'),
    ]

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount2': self.discount2,
            'discount3': self.discount3,
        })
        return res

    @api.depends('discount2', 'discount3')
    def _get_price_reduce(self):
        for line in self:
            super(SaleOrderLine, line)._get_price_reduce()
            if line.discount2:
                line.price_reduce *= (1 - line.discount2 / 100)
            if line.discount3:
                line.price_reduce *= (1 - line.discount3 / 100)
