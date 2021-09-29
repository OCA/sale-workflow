# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()
        else:
            raise ValidationError(
                _("Sale order line %s has unknown discounting type %s")
                % (self.name, self.discounting_type)
            )

    def _additive_discount(self):
        self.ensure_one()
        discount = sum([getattr(self, x) or 0.0 for x in self._discount_fields()])
        if discount <= 0:
            return 0
        elif discount >= 100:
            return 100
        return discount

    def _multiplicative_discount(self):
        self.ensure_one()
        discounts = [1 - (self[x] or 0.0) / 100 for x in self._discount_fields()]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return 100 - final_discount * 100

    def _discount_fields(self):
        return ["discount", "discount2", "discount3"]

    @api.depends("discount2", "discount3", "discounting_type")
    def _compute_amount(self):
        prev_values = self.triple_discount_preprocess()
        super()._compute_amount()
        self.triple_discount_postprocess(prev_values)

    discount2 = fields.Float(
        string="Disc. 2 (%)",
        digits="Discount",
        default=0.0,
    )
    discount3 = fields.Float(
        string="Disc. 3 (%)",
        digits="Discount",
        default=0.0,
    )
    discounting_type = fields.Selection(
        string="Discounting type",
        selection=[("additive", "Additive"), ("multiplicative", "Multiplicative")],
        default="multiplicative",
        required=True,
        help="Specifies whether discounts should be additive "
        "or multiplicative.\nAdditive discounts are summed first and "
        "then applied.\nMultiplicative discounts are applied sequentially.\n"
        "Multiplicative discounts are default",
    )

    _sql_constraints = [
        (
            "discount2_limit",
            "CHECK (discount2 <= 100.0)",
            "Discount 2 must be lower than 100%.",
        ),
        (
            "discount3_limit",
            "CHECK (discount3 <= 100.0)",
            "Discount 3 must be lower than 100%.",
        ),
    ]

    def _get_triple_discount(self):
        """Get the discount that is equivalent to the subsequent application
        of discount, discount2 and discount3"""
        discount_factor = 1.0
        for discount in [self.discount, self.discount2, self.discount3]:
            discount_factor *= (100.0 - discount) / 100.0
        return 100.0 - (discount_factor * 100.0)

    def _prepare_invoice_line(self, **kwargs):
        res = super()._prepare_invoice_line(**kwargs)
        res.update({"discount2": self.discount2, "discount3": self.discount3})
        return res

    @api.depends("discount2", "discount3")
    def _get_price_reduce(self):
        prev_values = self.triple_discount_preprocess()
        super()._get_price_reduce()
        self.triple_discount_postprocess(prev_values)

    def triple_discount_preprocess(self):
        """Save the values of the discounts in a dictionary,
        to be restored in postprocess.
        Resetting discount2 and discount3 to 0.0 avoids issues if
        this method is called multiple times.
        Updating the cache provides consistency through recomputations."""
        prev_values = dict()
        self.invalidate_cache(
            fnames=["discount", "discount2", "discount3"], ids=self.ids
        )
        for line in self:
            prev_values[line] = dict(
                discount=line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            line._cache.update(
                {
                    "discount": line._get_final_discount(),
                    "discount2": 0.0,
                    "discount3": 0.0,
                }
            )
        return prev_values

    @api.model
    def triple_discount_postprocess(self, prev_values):
        """Restore the discounts of the lines in the dictionary prev_values.
        Updating the cache provides consistency through recomputations."""
        self.invalidate_cache(
            fnames=["discount", "discount2", "discount3"],
            ids=[line.id for line in list(prev_values.keys())],
        )
        for line, prev_vals_dict in list(prev_values.items()):
            line._cache.update(prev_vals_dict)
