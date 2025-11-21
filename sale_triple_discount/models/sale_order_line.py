# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # core discount field is now a computed field
    # based on the 3 discounts defined below.
    # the digits limitation is removed, to make
    # the computation of the subtotal exact.
    # For exemple, if discounts are 05%, 09% and 13%
    # the main discount is 24.7885 % (and not 24.79)
    discount = fields.Float(
        string="Total Disc (%)",
        compute="_compute_discount",
        inverse="_inverse_discount",
        store=True,
        readonly=True,
        digits=None,
    )
    discount1 = fields.Float(
        compute="_compute_discounts",
        precompute=True,
        store=True,
        readonly=False,
        string="Disc. 1 (%)",
        digits="Discount",
        default=0.0,
    )
    discount2 = fields.Float(
        compute="_compute_discounts",
        precompute=True,
        store=True,
        readonly=False,
        string="Disc. 2 (%)",
        digits="Discount",
        default=0.0,
    )
    discount3 = fields.Float(
        compute="_compute_discounts",
        precompute=True,
        store=True,
        readonly=False,
        string="Disc. 3 (%)",
        digits="Discount",
        default=0.0,
    )
    discounting_type = fields.Selection(
        selection=[("additive", "Additive"), ("multiplicative", "Multiplicative")],
        default="multiplicative",
        required=True,
        help="Specifies whether discounts should be additive "
        "or multiplicative.\nAdditive discounts are summed first and "
        "then applied.\nMultiplicative discounts are applied sequentially.\n"
        "Multiplicative discounts are default",
    )

    @api.constrains("discounting_type")
    def _discounting_type_additive_not_allowed(self):
        # FIXME: see https://github.com/OCA/sale-workflow/issues/3649
        if any(rec.discounting_type == "additive" for rec in self):
            raise ValidationError(
                self.env._(
                    "Additive discount type is not fully implemented."
                    " See https://github.com/OCA/sale-workflow/issues/3649 "
                )
            )

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()
        else:
            raise ValidationError(
                self.env._(
                    "Sale order line %(name)s has unknown discounting type "
                    "%(disc_type)s",
                    name=self.name,
                    disc_type=self.discounting_type,
                )
            )

    def _additive_discount(self):
        self.ensure_one()
        discount = sum(self[x] or 0.0 for x in self._discount_fields())
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

    @api.model
    def _discount_fields(self):
        return ["discount1", "discount2", "discount3"]

    @api.depends("discount1", "discount2", "discount3", "discounting_type")
    def _compute_discount(self):
        res = super()._compute_discount()
        for rec in self:
            rec.discount = rec._get_final_discount()
        return res

    def _inverse_discount(self):
        for rec in self:
            rec.update({"discount1": rec.discount, "discount2": 0, "discount3": 0})

    @api.depends("discount")
    def _compute_discounts(self):
        # We intentionally call super to avoid triggering the full compute logic,
        # which would recalculate 'discount' from the three discount fields
        # At this stage, those fields may not be updated yet, and calling
        # _compute_discount() directly would overwrite the current value
        # calling super ensures the cache is coherent before applying the inverse
        super()._compute_discount()
        self._inverse_discount()
        return True

    _discount1_limit = models.Constraint(
        "CHECK (discount1 <= 100.0)",
        "Discount 1 must be lower or equal than 100%.",
    )
    _discount2_limit = models.Constraint(
        "CHECK (discount2 <= 100.0)",
        "Discount 2 must be lower or equal than 100%.",
    )
    _discount3_limit = models.Constraint(
        "CHECK (discount3 <= 100.0)",
        "Discount 3 must be lower or equal than 100%.",
    )

    def _prepare_invoice_line(self, **kwargs):
        """
        Inherit this method to bring
        more discount fields to the invoice lines
        """
        res = super()._prepare_invoice_line(**kwargs)
        res.update(
            {
                "discount1": self.discount1,
                "discount2": self.discount2,
                "discount3": self.discount3,
            }
        )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        order_lines = super().create(vals_list)
        lines_to_discount = order_lines
        for line, vals in zip(order_lines, vals_list, strict=False):
            if (line.discount != 0.0 or line.discount1 != 0.0) or (
                line.discount == 0.0
                and line.discount1 == 0.0
                and "discount1" in vals
                and vals["discount1"] == 0
            ):
                lines_to_discount -= line
        lines_to_discount._compute_discounts()
        return order_lines
