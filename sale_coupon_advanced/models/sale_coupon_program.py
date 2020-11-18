# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class SaleCouponProgram(models.Model):
    _inherit = "sale.coupon.program"

    is_cumulative = fields.Boolean(string="None-cumulative Promotion")
    reward_pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        domain=[("is_promotion_pricelist", "=", True)],
    )
    # Add possibility to use discount only on first order of a customer
    first_order_only = fields.Boolean(
        string="Apply only first",
        help="Apply only on the first order of each client matching the conditions",
    )

    next_n_customer_orders = fields.Integer(
        help="Maximum number of sales orders of the customer in which reward "
        "can be provided",
        string="Apply only on the next ",
        default=0,
    )
    is_reward_product_forced = fields.Boolean(
        string="Unordered product",
        default=False,
        help="If checked, the reward product will be added if not ordered.",
    )

    def _filter_programs_on_products(self, order):
        programs = super()._filter_programs_on_products(order)
        programs |= self.filtered(lambda r: r._is_program_forced())
        return programs

    def _filter_not_ordered_reward_programs(self, order):
        programs = super()._filter_not_ordered_reward_programs(order)
        programs_forced = self.filtered(lambda r: r._is_program_forced())
        programs_forced_code_needed = programs_forced.filtered(
            lambda r: r.promo_code_usage == "code_needed"
        )
        # No code promotions must be forced only specifically when it is
        # needed, to not duplicate promotions on each recompute.
        if self._context.get("force_not_ordered_no_code_reward_programs"):
            programs_forced_no_code = programs_forced.filtered(
                lambda r: r.promo_code_usage == "no_code_needed"
            )
            programs |= programs_forced - programs_forced_no_code
            # No code promotions must be added once, because no error is
            # raised for it being used already.
            for program_forced in programs_forced_no_code:
                if order.order_line.filtered(
                    lambda line: line.product_id == program_forced.reward_product_id
                ):
                    programs -= program_forced
                else:
                    programs |= program_forced
        return programs | programs_forced_code_needed

    def _check_promo_code(self, order, coupon_code):
        if self.first_order_only and not order.first_order():
            return {"error": _("This code can be used only for the first sale order!")}
        order_count = self._get_order_count(order)
        max_order_number = self.next_n_customer_orders
        if max_order_number and order_count >= max_order_number:
            return {
                "error": _("This code can be used only for the {} times!").format(
                    max_order_number
                )
            }
        res = super()._check_promo_code(order, coupon_code)
        return res

    @api.model
    def _filter_programs_from_common_rules(self, order, next_order=False):
        programs = super()._filter_programs_from_common_rules(order, next_order)
        programs = programs._filter_first_order_programs(order)
        programs = programs._filter_order_programs(
            order, self._filter_n_first_order_programs
        )
        return programs

    @api.constrains("next_n_customer_orders")
    def _constrains_first_n_orders_positive(self):
        for record in self:
            if record.next_n_customer_orders < 0:
                raise exceptions.ValidationError(
                    _("`Apply only on the next` should not be a negative value.")
                )

    def _get_partner_order_line_count_domain(self, order):
        self.ensure_one()
        partner_id = order.partner_id.commercial_partner_id.id
        return [
            ("product_id", "=", self.discount_line_product_id.id),
            ("order_id.partner_id.commercial_partner_id", "=", partner_id),
            ("order_id.state", "!=", "cancel"),
        ]

    def _get_order_count(self, order):
        self.ensure_one()
        domain = self._get_partner_order_line_count_domain(order)
        data = self.env["sale.order.line"].read_group(
            domain, ["order_id"], ["order_id"]
        )
        return sum(m["order_id_count"] for m in data)

    @api.model
    def _filter_first_order_programs(self, order):
        """
        Filter programs where first_order_only is True,
        and the customer have already ordered before.
        """
        first_ord = order.first_order()
        return self.filtered(
            lambda self: (self.first_order_only and first_ord)
            or not (self.first_order_only and first_ord)
        )

    @api.model
    def _filter_n_first_order_programs(self, program, order):
        """
        Filter programs where next_n_customer_orders is set, and
        the max number of orders have already been reached by the customer.
        """
        return not (
            program.next_n_customer_orders
            and program._get_order_count(order) >= program.next_n_customer_orders
        )

    def _filter_order_programs(self, order, predicate):
        filtered_programs = self.env[self._name]
        for program in self:
            if not predicate(program, order):
                continue
            filtered_programs |= program
        return filtered_programs

    def _is_program_forced(self):
        self.ensure_one()
        return (
            self.is_reward_product_forced
            # Extra checks to make sure it is only applied for promotion
            # product rewards.
            and self.program_type == "promotion_program"
            and self.reward_type == "product"
        )


class SaleCouponReward(models.Model):
    _inherit = "sale.coupon.reward"

    reward_type = fields.Selection(selection_add=[("use_pricelist", "Pricelist")])


class SaleCoupon(models.Model):
    _inherit = "sale.coupon"

    reward_pricelist_id = fields.Many2one(
        related="program_id.reward_pricelist_id", string="Pricelist"
    )
