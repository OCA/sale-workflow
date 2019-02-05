# -*- coding: utf-8 -*-
# Copyright 2019 Sylvain Van Hoof (Okia SPRL) <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO with discounts.
        Copy/paste from standard method in sale
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == \
                        'round_globally':
                    price_reduce = line.price_reduce  # Use the price reduced
                    taxes = line.tax_id.compute_all(
                        price_reduce,
                        currency=line.order_id.currency_id,
                        quantity=line.product_uom_qty,
                        product=line.product_id,
                        partner=order.partner_shipping_id
                    )
                    amount_tax += sum(
                        t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed':
                    order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
