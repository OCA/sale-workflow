# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
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
        store=True,
        readonly=True,
        digits=None,
    )
    discount1 = fields.Float(
        string="Disc. 1 (%)",
        digits="Discount",
        default=0.0,
    )
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
                _(
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
                _("Sale order line %(name)s has unknown discounting type %(dic_type)s")
                % {"name": self.name, "disc_type": self.discounting_type}
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
        for rec in self:
            rec.discount = rec._get_final_discount()

    _sql_constraints = [
        (
            "discount1_limit",
            "CHECK (discount1 <= 100.0)",
            "Discount 1 must be lower or equal than 100%.",
        ),
        (
            "discount2_limit",
            "CHECK (discount2 <= 100.0)",
            "Discount 2 must be lower or equal than 100%.",
        ),
        (
            "discount3_limit",
            "CHECK (discount3 <= 100.0)",
            "Discount 3 must be lower or equal than 100%.",
        ),
    ]

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
