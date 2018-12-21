# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('discount2', 'discount3')
    def _compute_amount(self):
        prev_values = self.triple_discount_preprocess()
        super(SaleOrderLine, self)._compute_amount()
        self.triple_discount_postprocess(prev_values)

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

    def _get_triple_discount(self):
        """Get the discount that is equivalent to the subsequent application
        of discount, discount2 and discount3"""
        discount_factor = 1.0
        for discount in [self.discount, self.discount2, self.discount3]:
            discount_factor *= (100.0 - discount) / 100.0
        return 100.0 - (discount_factor * 100.0)

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount2': self.discount2,
            'discount3': self.discount3,
        })
        return res

    @api.depends('discount2', 'discount3')
    def _get_price_reduce(self):
        prev_values = self.triple_discount_preprocess()
        super(SaleOrderLine, self)._get_price_reduce()
        self.triple_discount_postprocess(prev_values)

    @api.multi
    def triple_discount_preprocess(self):
        """Save the values of the discounts in a dictionary,
        to be restored in postprocess.
        Resetting discount2 and discount3 to 0.0 avoids issues if
        this method is called multiple times.
        Updating the cache provides consistency through recomputations."""
        prev_values = dict()
        self.invalidate_cache(
            fnames=['discount', 'discount2', 'discount3'],
            ids=self.ids)
        for line in self:
            prev_values[line] = dict(
                discount=line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            line._cache.update({
                'discount': line._get_triple_discount(),
                'discount2': 0.0,
                'discount3': 0.0
            })
        return prev_values

    @api.model
    def triple_discount_postprocess(self, prev_values):
        """Restore the discounts of the lines in the dictionary prev_values.
        Updating the cache provides consistency through recomputations."""
        self.invalidate_cache(
            fnames=['discount', 'discount2', 'discount3'],
            ids=[l.id for l in prev_values.keys()])
        for line, prev_vals_dict in prev_values.items():
            line._cache.update(prev_vals_dict)
