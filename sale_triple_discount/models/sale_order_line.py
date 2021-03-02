# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 ~ 2021 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["line.triple_discount.mixin", "sale.order.line"]

    @api.depends('discount2', 'discount3', 'discounting_type')
    def _compute_amount(self):
        for line in self:
            prev_values = line.triple_discount_preprocess()
            super(SaleOrderLine, line)._compute_amount()
            line.triple_discount_postprocess(prev_values)

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
