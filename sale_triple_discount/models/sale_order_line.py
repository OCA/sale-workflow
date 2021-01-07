# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()

    def _additive_discount(self):
        self.ensure_one()
        discount = sum(
            [getattr(self, x) or 0.0 for x in self._discount_fields()]
        )
        if discount <= 0:
            return 0
        elif discount >= 100:
            return 100
        return discount

    def _multiplicative_discount(self):
        self.ensure_one()
        discounts = [1 - (self[x] or 0.0) / 100
                     for x in self._discount_fields()]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return 100 - final_discount * 100

    def _discount_fields(self):
        return ['discount', 'discount2', 'discount3']

    @api.depends('discount2', 'discount3', 'discounting_type')
    def _compute_amount(self):
        for line in self:
            prev_price_unit = line.price_unit
            prev_discount = line.discount
            price_unit = line.price_unit * (
                1 - (line._get_final_discount() or 0.0) / 100.0
            )
            line.update({"price_unit": price_unit, "discount": 0.0})
            super(SaleOrderLine, line)._compute_amount()
            line.update({"price_unit": prev_price_unit, "discount": prev_discount})

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
    discounting_type = fields.Selection(
        string="Discounting type",
        selection=[
            ('additive', 'Additive'),
            ('multiplicative', 'Multiplicative'),
        ],
        default="multiplicative",
        required=True,
        help="Specifies whether discounts should be additive "
        "or multiplicative.\nAdditive discounts are summed first and "
        "then applied.\nMultiplicative discounts are applied sequentially.\n"
        "Multiplicative discounts are default",
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
        for line in self:
            super(SaleOrderLine, line)._get_price_reduce()
            line.price_reduce = line.price_unit * (
                1 - (line._get_final_discount() or 0.0) / 100.0
            )
