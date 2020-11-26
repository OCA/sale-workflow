# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import pickle

from odoo import api, fields, models


def _pickle_copy(data):
    """Do deep copy of specified data."""
    # Seems to work much faster for small data than copy.deepcopy.
    return pickle.loads(pickle.dumps(data))


class SaleCoupon(models.Model):
    """Extend to implement multi use coupon rule."""

    _inherit = "sale.coupon"

    # Takes value from related program (coupon_multi_use field), when
    # it is generated.
    multi_use = fields.Boolean(readonly=True)
    currency_program_id = fields.Many2one(related="program_id.currency_id")
    consumption_line_ids = fields.One2many(
        "sale.coupon.consumption_line", "coupon_id", "Consumption Lines", readonly=True,
    )
    discount_fixed_amount_delta = fields.Monetary(
        "Fixed Amount Delta",
        compute="_compute_discount_fixed_amount_delta",
        currency_field="currency_program_id",
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

    def _filter_multi_use_triggered(self, vals):
        # Indicating for coupon to be consumed
        if vals.get("state") == "used":
            return self.filtered(
                # Must have amount to split.
                lambda r: r.multi_use
                and r.discount_fixed_amount_delta > 0
            )
        return self.env[self._name]

    def _get_related_sale_order_line(self, sale_order):
        self.ensure_one()
        discount_product = self.program_id.discount_line_product_id
        # Supposed to be only one such line.
        return sale_order.order_line.filtered(
            lambda r: r.product_id == discount_product
        )[0]

    def _prepare_consumption_line(self, sale_order_line):
        self.ensure_one()
        program = self.program_id
        from_currency = sale_order_line.order_id.pricelist_id.currency_id
        to_currency = program.currency_id
        amount = from_currency._convert(
            abs(sale_order_line.price_total),
            to_currency,
            # program company is not mandatory, so fallback to user
            # company.
            program.company_id or self.env.user.company_id,
            # Symmetrical -> program discount is also converted to SO
            # amount using today.
            fields.Date.today(),
        )
        return {
            "coupon_id": self.id,
            "amount": amount,
            "sale_order_line_id": sale_order_line.id,
        }

    def _create_consumption_line(self, sale_order_line):
        vals = self._prepare_consumption_line(sale_order_line)
        return self.env["sale.coupon.consumption_line"].create(vals)

    def _handle_multi_use(self, coupon_sale_order):
        self.ensure_one()
        related_sol = self._get_related_sale_order_line(coupon_sale_order)
        if related_sol not in self.consumption_line_ids.mapped("sale_order_line_id"):
            self._create_consumption_line(related_sol)
        return self.discount_fixed_amount_delta > 0

    def _handle_multi_use_reset(self, coupon_sale_order):
        consumption_lines = self.mapped("consumption_line_ids")
        consumption_lines._unlink_consumption_lines(
            coupon_sale_order.mapped("order_line")
        )

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
        """Extend to manage multi_use coupons.

        Each coupon record is handled separately, because some might
        be valid, some not after handling multi use.
        """
        coupon_sale_order = self._context.get("coupon_sale_order")
        other_coupons = self  # by default all coupons.
        if coupon_sale_order:
            multi_use_coupons = self._filter_multi_use_triggered(vals)
            other_coupons = self - multi_use_coupons
            for multi_use_coupon in multi_use_coupons:
                copied_vals = _pickle_copy(vals)
                coupon_still_valid = multi_use_coupon._handle_multi_use(
                    coupon_sale_order
                )
                if coupon_still_valid:
                    # Not marking it as consumed.
                    del copied_vals["state"]
                if copied_vals:  # could be empty dict, so no point writing
                    super(SaleCoupon, multi_use_coupon).write(copied_vals)
            # If coupon is set back to valid, we need to remove
            # consumption lines that were used on that specific SO.
            if vals.get("state") == "new":
                self._handle_multi_use_reset(coupon_sale_order)
        return super(SaleCoupon, other_coupons).write(vals)
