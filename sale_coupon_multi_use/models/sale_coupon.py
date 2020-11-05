from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleCoupon(models.Model):
    """Extend to implement multi use coupon rule."""

    _inherit = "sale.coupon"

    # Takes value from related program (coupon_multi_use field), when
    # it is generated.
    multi_use = fields.Boolean("Multi Use", readonly=True)
    consumption_line_ids = fields.One2many(
        "sale.coupon.consumption_line", "coupon_id", "Consumption Lines", readonly=True,
    )
    discount_fixed_amount_delta = fields.Float(
        "Fixed Amount Delta", compute="_compute_discount_fixed_amount_delta"
    )

    def _get_discount_fixed_amount_delta(self):
        self.ensure_one()
        amount_total = self.program_id.discount_fixed_amount
        amount_consumed = sum(self.consumption_line_ids.mapped("amount"))
        return amount_total - amount_consumed

    @api.depends("program_id.discount_fixed_amount", "consumption_line_ids.amount")
    def _compute_discount_fixed_amount_delta(self):
        for rec in self:
            rec.discount_fixed_amount_delta = rec._get_discount_fixed_amount_delta()

    def _is_multi_use_triggered(self, vals):
        # We expect multi_use coupon will be updated one by one only.
        return (
            len(self) == 1
            and self.multi_use
            # Must have amount to split.
            and self.discount_fixed_amount_delta > 0
            # Indicating for coupon to be consumed.
            and vals.get("state") == "used"
        )

    def _get_compared_discount_with_delta(self, coupon_order_data):
        sale_order = coupon_order_data["order"]
        amount_total_orig = coupon_order_data["amount_total"]
        discount = amount_total_orig - sale_order.amount_total
        new_delta = self.discount_fixed_amount_delta - discount
        return new_delta, discount

    def _adjust_discount_on_sale_order(self, order, amount_to_adjust):
        self.ensure_one()
        discount_product = self.program_id.discount_line_product_id
        # Supposed to be only one such line.
        coupon_line = order.order_line.filtered(
            lambda r: r.product_id == discount_product
        )
        coupon_line.price_unit += amount_to_adjust

    def _get_related_sale_order_line(self, sale_order):
        self.ensure_one()
        discount_product = self.program_id.discount_line_product_id
        # Supposed to be only one such line.
        return sale_order.order_line.filtered(
            lambda r: r.product_id == discount_product
        )[0]

    def _prepare_consumption_line(self, amount_consumed, sale_order):
        self.ensure_one()
        line = self._get_related_sale_order_line(sale_order)
        return {
            "coupon_id": self.id,
            "amount": amount_consumed,
            "sale_order_line_id": line.id,
        }

    def _create_consumption_line(self, amount_consumed, sale_order):
        vals = self._prepare_consumption_line(amount_consumed, sale_order)
        return self.env["sale.coupon.consumption_line"].create(vals)

    def _consume_line(self, discount, sale_order):
        self.ensure_one()
        amount_consumed = min(discount, self.discount_fixed_amount_delta)
        consumption_line = self._create_consumption_line(amount_consumed, sale_order)
        consumption_line._normalize_discount()
        return consumption_line

    def _handle_multi_use(self, coupon_order_data):
        self.ensure_one()
        new_delta, discount = self._get_compared_discount_with_delta(coupon_order_data)
        self._consume_line(discount, coupon_order_data["order"])
        # Indicates whether coupon was fully consumed.
        return new_delta <= 0

    @api.model_create_multi
    def create(self, vals_list):
        """Extend to pick up coupon_multi_use value from program."""
        for vals in vals_list:
            multi_use = (
                self.env["sale.coupon.program"]
                .browse(vals.get("program_id"))
                .coupon_multi_use
            )
            if "multi_use" not in vals:
                vals["multi_use"] = multi_use
        return super().create(vals_list)

    def write(self, vals):
        """Extend to manage multi_use coupons."""
        if self._is_multi_use_triggered(vals):
            coupon_order_data = self._context.get("coupon_order_data")
            if coupon_order_data:
                coupon_consumed = self._handle_multi_use(coupon_order_data)
                if not coupon_consumed:
                    # Makes it so coupon that coupon is not used up yet.
                    del vals["state"]
        return super().write(vals)


class SaleCouponConsumptionLine(models.Model):
    """Model that stores data for single coupon multiple uses."""

    _name = "sale.coupon.consumption_line"
    _description = "Sale Coupon Consumption Line"

    coupon_id = fields.Many2one("sale.coupon", "Coupon", required=True, index=True)
    # ondelete takes care of automatically removing consumption line,
    # when discount line is removed on related sale order.
    sale_order_line_id = fields.Many2one(
        "sale.order.line", "Sale Order Line", required=True, ondelete="cascade"
    )
    amount = fields.Float()

    def _normalize_discount(self):
        """Adjust SOL discount to match consumed discount."""
        self.ensure_one()
        # Discount initially won't match, when standard functionality
        # applies full discount from coupon. But because we split
        # coupon amount, we want to apply maximum possible discount.
        sol = self.sale_order_line_id
        sol_discount = abs(sol.price_unit)
        amount_to_adjust = sol_discount - self.amount
        if amount_to_adjust > 0:
            # Reducing negative amount here.
            sol.price_unit += amount_to_adjust

    def unlink(self):
        """Override to prevent direct unlink."""
        if not self._context.get("force_unlink_coupon_consumption_lines"):
            raise UserError(
                _(
                    "Consumption Lines can't be deleted directly. To do that, "
                    "delete related sale order line."
                )
            )
        return super().unlink()
