# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.tools import float_compare


class SaleCoupon(models.Model):
    """Extend to implement multi use coupon rule."""

    _inherit = "sale.coupon"

    multi_use = fields.Boolean(related="program_id.coupon_multi_use")
    currency_program_id = fields.Many2one(related="program_id.currency_id")
    consumption_line_ids = fields.One2many(
        comodel_name="sale.coupon.consumption_line",
        inverse_name="coupon_id",
        readonly=True,
    )
    discount_fixed_amount_delta = fields.Float(
        compute="_compute_discount_fixed_amount_delta",
        digits="Product Price",
        currency_field="currency_program_id",
        string="Fixed Amount Delta",
    )
    sale_multi_use_ids = fields.Many2many(
        comodel_name="sale.order",
        compute="_compute_sale_multi_use_ids",
        string="Applied on Orders",
    )

    @api.depends("program_id.discount_fixed_amount", "consumption_line_ids.amount")
    def _compute_discount_fixed_amount_delta(self):
        for rec in self:
            amount_total = rec.program_id.discount_fixed_amount
            amount_already_consumed = sum(rec.consumption_line_ids.mapped("amount"))
            rec.discount_fixed_amount_delta = amount_total - amount_already_consumed

    @api.depends("consumption_line_ids")
    def _compute_sale_multi_use_ids(self):
        for rec in self:
            rec.sale_multi_use_ids = rec.mapped(
                "consumption_line_ids.sale_order_line_id.order_id"
            )

    def _check_coupon_code(self, order):
        # Same check as is for `applied_coupon_ids` field.
        if self.program_id in order.mapped("coupon_multi_use_ids.program_id"):
            return {
                "error": _("Multi-Use Coupon is already applied for the same reward")
            }
        return super()._check_coupon_code(order)

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

    def _create_consumption_line(self, sale_order):
        sale_order_line = self._get_related_sale_order_line(sale_order)
        vals = self._prepare_consumption_line(sale_order_line)
        return self.env["sale.coupon.consumption_line"].create(vals)

    def move_to_multi_use(self):
        self.ensure_one()
        # Create consumption line from sale order
        self._create_consumption_line(self.sales_order_id)
        # Coupon apply code wizard set the sale order on sales_order_id,
        # but for multi-use coupon, we can't use and don't need this M2O field.
        self.sales_order_id = False
        self.check_and_update_coupon_state()

    def check_and_update_coupon_state(self):
        """Set coupons state depending of discount_fixed_amount_delta."""
        for coupon in self:
            digits = self.env["decimal.precision"].precision_get(
                coupon._fields["discount_fixed_amount_delta"]._digits
            )
            # Coupon must be consumed only if not remaining delta
            delta = coupon.discount_fixed_amount_delta
            remaining_delta = float_compare(delta, 0, precision_digits=digits) > 0
            if coupon.state == "new" and not remaining_delta:
                coupon.state = "used"
            elif coupon.state == "used" and remaining_delta:
                coupon.state = "new"
