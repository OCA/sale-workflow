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

    discount = fields.Float(
        string="Total discount",
        store=True,
        compute="_compute_discount",
        compute_sudo=True,
        precompute=True,
    )
    discount1 = fields.Float(
        string="Discount 1 (%)",
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

    @api.depends(
        lambda self: self._get_multiple_discount_field_names()
        + ["product_id", "product_uom", "product_uom_qty"]
    )
    def _compute_discount(self):
        # Base Odoo just continues instead of assigning to 0 in this case
        # but we depend on the super() value resetting to a discount unpolluted
        # by the extra fields before taking them into account
        for line in self:
            if not (
                line.order_id.pricelist_id
                and line.order_id.pricelist_id.discount_policy == "without_discount"
            ):
                line.discount = 0
        res = super()._compute_discount()
        if self.env.context.get("skip_triple_discount"):
            return res
        for line in self._get_lines_to_compute_discount():
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

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()
        else:
            raise ValidationError(
                _("Sale order line %(name)s has unknown discounting type %(dic_type)s")
                % {"name": self.name, "dic_type": self.discounting_type}
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
