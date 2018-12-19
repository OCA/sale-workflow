# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        prev_values = dict()
        for order in self:
            for line in order.order_line:
                prev_values[line] = dict(
                    discount=line.discount,
                    discount2=line.discount2,
                    discount3=line.discount3,
                )
                # Update, for some reason, does not work
                line.write({
                    'discount': line._get_triple_discount(),
                    'discount2': 0.0,
                    'discount3': 0.0
                })
        super(SaleOrder, self)._amount_all()

        # Restore previous values
        for line, prev_vals_dict in prev_values.items():
            # Update, for some reason, does not work
            line.write(prev_vals_dict)
