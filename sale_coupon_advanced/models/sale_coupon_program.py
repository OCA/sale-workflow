# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


def _predicate_promo_code(program, order, coupon_code):
    return bool(program.filtered(lambda r: r.promo_code == coupon_code))


def _predicate_no_code_needed(program, order, coupon_code):
    return program.promo_code_usage == "no_code_needed"


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
        help="Maximum number of sales orders of the customer in which reward \
         can be provided",
        string="Apply only on the next ",
        default=0,
    )
    is_reward_product_forced = fields.Boolean(
        string="Unordered product",
        default=False,
        help="If checked, the reward product will be added if not ordered.",
    )

    def _check_promo_code_forced(self, order, coupon_code=None, predicate=None):
        def default_predicate(program, order, coupon_code):
            return True

        if not predicate:
            predicate = default_predicate
        # Using same check again, to know which error was returned. Can't
        # use error message, because it is unstable check. Message can
        # be translated and it would then return different text than
        # expected.
        # Can also use extra predicate to further filter program.
        return (
            self.is_reward_product_forced
            and self.promo_applicability == "on_current_order"
            and self.reward_type == "product"
            and not order._is_reward_in_order_lines(self)
            and predicate(self, order, coupon_code)
        )

    def _check_promo_code(self, order, coupon_code):
        if self.first_order_only and not order.first_order():
            return {"error": _("Coupon can be used only for the first sale order!")}
        order_count = self._get_order_count(order)
        max_order_number = self.next_n_customer_orders
        if max_order_number and order_count >= max_order_number:
            return {
                "error": _("Coupon can be used only for the {} times!").format(
                    max_order_number
                )
            }
        res = super()._check_promo_code(order, coupon_code)
        if res.get("error") and self._check_promo_code_forced(
            order, coupon_code=coupon_code, predicate=_predicate_promo_code
        ):
            return {}
        return res

    @api.model
    def _filter_programs_from_common_rules(self, order, next_order=False):
        # FIXME: this is not great, because this method responsibility
        # is to just filter programs, not silently create lines.
        for program in self:
            order._filter_force_create_counter_line_for_reward_product(
                program,
                # This call is only meant for auto applied promotions.
                predicate=_predicate_no_code_needed,
            )
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


class SaleCouponReward(models.Model):
    _inherit = "sale.coupon.reward"

    reward_type = fields.Selection(selection_add=[("use_pricelist", "Pricelist")])


class SaleCoupon(models.Model):
    _inherit = "sale.coupon"

    reward_pricelist_id = fields.Many2one(
        related="program_id.reward_pricelist_id", string="Pricelist"
    )
