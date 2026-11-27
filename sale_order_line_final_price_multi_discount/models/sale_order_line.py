# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero, float_round, str2bool

POLICY_PARAM = "sale_order_line_final_price_multi_discount.distribution_policy"
UNLOCK_PARAM = "sale_order_line_final_price_multi_discount.unlock_prices"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # ``discount`` is computed from ``discount_distribution`` by its own method
    # (sale_multi_discount), so the dependency on ``price_final`` that
    # sale_order_line_final_price declares on ``_compute_discount`` never
    # reaches it. The final price is resolved into the distribution instead:
    # by this inverse when the line is written, by the onchange below while it
    # is edited in the form.
    price_final = fields.Float(inverse="_inverse_price_final")

    def _compute_price_edit_allowed(self):
        res = super()._compute_price_edit_allowed()
        unlock = self.env["ir.config_parameter"].sudo().get_param(UNLOCK_PARAM)
        if str2bool(unlock or "", default=False):
            self.price_edit_allowed = True
        return res

    def _inverse_price_final(self):
        self._apply_price_final()

    @api.onchange("price_final")
    def _onchange_price_final(self):
        self._apply_price_final()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        with_final = lines.browse(
            line.id
            for line, vals in zip(lines, vals_list, strict=True)
            if "price_final" in vals
        )
        if with_final:
            # The precomputed discount and amounts were protected while the
            # inverse moved the distribution: they still are the ones of the
            # pricelist.
            with_final.modified(["discount_distribution"])
            with_final._recompute_price_final()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if "price_final" in vals:
            self._recompute_price_final()
        return res

    def _recompute_price_final(self):
        # The final price was protected while being set: once the discount is
        # rounded, let it show what the line is really worth.
        self.env.add_to_compute(self._fields["price_final"], self)

    def _apply_price_final(self):
        """Move the discounts so that the line net price meets the final one."""
        dp = self.env["decimal.precision"].precision_get("Product Price")
        for line in self:
            if line.display_type or not float_compare(
                line.price_final, line._get_discounted_price(), precision_digits=dp
            ):
                continue
            line._set_discount_to_reach(line._get_price_final_reach(line.price_final))

    def _get_price_final_reach(self, price):
        """Net price the discount distribution alone has to reach for the line
        to be worth ``price``. Hook for the modules that fold other amounts
        into the line discount on top of the distribution."""
        self.ensure_one()
        return price

    def _set_discount_to_reach(self, price):
        """Bring the unit price to ``price`` by moving the discounts only.

        With no catalog price to discount from (no technical unit price, or a
        zero unit price) no discount can reach the figure: ``price`` becomes
        the unit price and the line carries no discount, as in
        sale_order_line_final_price.
        """
        self.ensure_one()
        dp = self.env["decimal.precision"].precision_get("Product Price")
        if not self.technical_price_unit or float_is_zero(
            self.price_unit, precision_digits=dp
        ):
            self.price_unit = price
            self.discount_distribution = []
            return
        self.discount_distribution = self._prepare_price_final_distribution(
            (1 - price / self.price_unit) * 100
        )

    def _prepare_price_final_distribution(self, discount):
        """Return the discount distribution whose aggregate is ``discount``."""
        self.ensure_one()
        policy = (
            self.env["ir.config_parameter"].sudo().get_param(POLICY_PARAM) or "replace"
        )
        if policy == "append" and self.product_id:
            base = self._get_pricelist_discount_distribution()
            base_factor = (
                1
                - self.env["account.move.line"]._aggregate_discount_distribution(base)
                / 100
            )
            if base and not float_is_zero(base_factor, precision_digits=6):
                residual = self._round_price_final_discount(
                    (1 - (1 - discount / 100) / base_factor) * 100
                )
                return list(base) + [residual] if residual else list(base)
        discount = self._round_price_final_discount(discount)
        return [discount] if discount else []

    def _round_price_final_discount(self, discount):
        digits = self.env["decimal.precision"].precision_get("Discount")
        # Drop the float noise of the division first, otherwise rounding up
        # would turn 13.000000000000002 into 13.01.
        discount = float_round(discount, precision_digits=digits + 4)
        return float_round(
            discount,
            precision_digits=digits,
            rounding_method=self._get_price_final_discount_rounding_method(discount),
        )

    def _get_price_final_discount_rounding_method(self, discount):
        """Rounding method of a discount worked out of a final price."""
        return "HALF-UP"
