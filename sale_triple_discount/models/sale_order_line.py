# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "triple.discount.mixin"]

    # core discount field is now a computed field
    # based on the 3 discounts defined below.
    # the digits limitation is removed, to make
    # the computation of the subtotal exact.
    # For exemple, if discounts are 05%, 09% and 13%
    # the main discount is 24.7885 % (and not 24.79)
    discount = fields.Float(
        string="Total Disc (%)",
        store=True,
        compute="_compute_discount",
        compute_sudo=True,
        precompute=True,
    )
    discount1 = fields.Float(
        string="Disc. 1 (%)",
        digits="Discount",
        compute="_compute_discount1",
        store=True,
        compute_sudo=True,
        precompute=True,
        readonly=False,
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
        discount = sum(
            self[x] or 0.0 for x in self._get_multiple_discount_field_names()
        )
        if discount <= 0:
            return 0
        elif discount >= 100:
            return 100
        return discount

    def _multiplicative_discount(self):
        self.ensure_one()
        return self._get_aggregated_multiple_discounts(
            [self[x] for x in self._get_multiple_discount_field_names()]
        )

    @api.depends(
        lambda self: self._get_multiple_discount_field_names()
        + ["product_id", "product_uom", "product_uom_qty"]
    )
    def _compute_discount(self):
        # Base Odoo just continues instead of assigning to 0 in this case
        # but we depend on the super() value resetting to a discount unpolluted
        # by the extra fields before taking them into account
        discount_enabled = self.env[
            "product.pricelist.item"
        ]._is_discount_feature_enabled()
        for line in self:
            if not (line.order_id.pricelist_id and discount_enabled):
                line.discount = 0
        res = super()._compute_discount()
        if self.env.context.get("skip_triple_discount"):
            return res
        for line in self:
            line.discount = line._get_final_discount()
        return res

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount1(self):
        # Calculate the original super()s discount and drag it to discount1
        # This is primarily for the field to visually update when creating new lines
        # rather than updating itself in the create() after you save
        # Since we aren't in the actual compute, this shouldn't actually save any
        # values to .discount
        with self.env.protecting(
            [self.env["sale.order.line"]._fields["discount"]], self
        ):
            self.with_context(skip_triple_discount=True)._compute_discount()
            for line in self:
                line.discount1 = line.discount

    def _prepare_invoice_line(self, **kwargs):
        """
        Inherit this method to bring
        more discount fields to the invoice lines
        """
        res = super()._prepare_invoice_line(**kwargs)
        res.pop("discount", None)
        if self.discounting_type == "multiplicative":
            res.update(
                {
                    "discount1": self.discount1,
                    "discount2": self.discount2,
                    "discount3": self.discount3,
                }
            )
        else:
            res.update({"discount1": self.discount})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        order_lines = super().create(vals_list)
        lines_to_discount = self.env["sale.order.line"]
        for line, vals in zip(order_lines, vals_list, strict=True):
            if "discount" in vals and vals["discount"] == 0:
                lines_to_discount |= line
        lines_to_discount.write({"discount1": 0.0, "discount2": 0.0, "discount3": 0.0})
        return order_lines
