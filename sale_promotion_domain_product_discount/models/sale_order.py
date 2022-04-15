from odoo import _, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_new_no_code_promo_reward_lines(self):
        """
        Override core method to save the program with new discount apply rule
        """
        self.ensure_one()
        order = self
        programs = order._get_applicable_no_code_promo_program()
        programs = (
            programs._keep_only_most_interesting_auto_applied_global_discount_program()
        )
        if any([program.reward_type == "discount_line" for program in programs]):
            for program in programs:
                error_status = program._check_promo_code(order, False)
                if not error_status.get("error"):
                    if program.promo_applicability == "on_next_order":
                        order.state != "cancel" and order._create_reward_coupon(program)
                    elif (
                        program.discount_line_product_id.id
                        not in self.order_line.mapped("product_id").ids
                    ):
                        if program.reward_type == "discount_line":
                            self._get_reward_line_values(program)
                        else:
                            self.write(
                                {
                                    "order_line": [
                                        (0, False, value)
                                        for value in self._get_reward_line_values(
                                            program
                                        )
                                    ]
                                },
                            )
                    order.no_code_promo_program_ids |= program
        else:
            super()._create_new_no_code_promo_reward_lines()

    def _get_reward_line_values(self, program):
        """
        Overrider core method to set discount for line if program has
        'discount_line' reward type
        """
        if program.reward_type == "discount_line":
            self._set_reward_discount_for_lines(program)
            return []
        else:
            return super(SaleOrder, self)._get_reward_line_values(program)

    def _set_reward_discount_for_lines(self, program):
        """
        Update discount field by program
        """
        discount = program.discount_percentage
        lines = self._get_paid_order_lines()
        if program.discount_apply_on == "cheapest_product":
            line = self._get_cheapest_line()
            if line:
                line.discount = discount
        elif program.discount_apply_on in ["specific_products", "on_order"]:
            if program.discount_apply_on == "specific_products":
                # We should not exclude reward line that offer this product
                # since we need to offer only the discount on
                # the real paid product (regular product - free product)
                free_product_lines = (
                    self.env["coupon.program"]
                    .search(
                        [
                            ("reward_type", "=", "product"),
                            (
                                "reward_product_id",
                                "in",
                                program.discount_specific_product_ids.ids,
                            ),
                        ],
                    )
                    .mapped("discount_line_product_id")
                )
                lines = lines.filtered(
                    lambda x: x.product_id
                    in (program.discount_specific_product_ids | free_product_lines),
                )
            for line in lines:
                line.discount = discount
        elif program.discount_apply_on == "domain_product":
            lines = (self.order_line - self._get_reward_lines()).filtered(
                lambda line: program._get_valid_products(line.product_id),
            )
            for line in lines:
                line.discount = discount

    def _get_reward_values_discount(self, program):
        """
        Override core method to check and apply new discount apply rule
        """
        if program.discount_type == "domain_product":
            lines = (self.order_line - self._get_reward_lines()).filtered(
                lambda line: program._get_valid_products(line.product_id),
            )
            # when processing lines we should not discount more than the order remaining total
            currently_discounted_amount = 0
            reward_dict = {}
            amount_total = sum(
                self._get_base_order_lines(program).mapped("price_subtotal")
            )
            for line in lines:
                discount_line_amount = min(
                    self._get_reward_values_discount_percentage_per_line(program, line),
                    amount_total - currently_discounted_amount,
                )
                if discount_line_amount:
                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]["price_unit"] -= discount_line_amount
                    else:
                        taxes = self.fiscal_position_id.map_tax(line.tax_id)
                        uom_id = program.discount_line_product_id.uom_id.id
                        reward_dict[line.tax_id] = {
                            "name": _(
                                "Discount: %(program)s - On product with following "
                                "taxes: %(taxes)s",
                                program=program.name,
                                taxes=", ".join(taxes.mapped("name")),
                            ),
                            "product_id": program.discount_line_product_id.id,
                            "price_unit": -discount_line_amount
                            if discount_line_amount > 0
                            else 0,
                            "product_uom_qty": 1.0,
                            "product_uom": uom_id,
                            "is_reward_line": True,
                            "tax_id": [(4, tax.id, False) for tax in taxes],
                        }
                        currently_discounted_amount += discount_line_amount

            # If there is a max amount for discount, we might have to limit
            # some discount lines or completely remove some lines
            max_amount = program._compute_program_amount(
                "discount_max_amount", self.currency_id
            )
            if max_amount > 0:
                amount_already_given = 0
                for val in list(reward_dict):
                    amount_to_discount = (
                        amount_already_given + reward_dict[val]["price_unit"]
                    )
                    if abs(amount_to_discount) > max_amount:
                        reward_dict[val]["price_unit"] = -(
                            max_amount - abs(amount_already_given)
                        )
                        add_name = formatLang(
                            self.env, max_amount, currency_obj=self.currency_id
                        )
                        reward_dict[val]["name"] += (
                            "( " + _("limited to ") + add_name + ")"
                        )
                    amount_already_given += reward_dict[val]["price_unit"]
                    if reward_dict[val]["price_unit"] == 0:
                        del reward_dict[val]
            return reward_dict.values()
        else:
            return super()._get_reward_values_discount(program)

    def _update_existing_reward_lines(self):
        """
        Override method to add context to ignore programs with reward type is discount_line
        """
        self.ensure_one()
        res = super(
            SaleOrder,
            self.with_context(ignore_reward_type_with_discount_line=True),
        )._update_existing_reward_lines()
        order = self
        applied_discount_programs = (
            order._get_applied_programs_with_rewards_on_current_order().filtered(
                lambda program: program.reward_type == "discount_line",
            )
        )
        for program in applied_discount_programs:
            lines = (self.order_line - self._get_reward_lines()).filtered(
                lambda line: program._get_valid_products(line.product_id),
            )
            lines.discount = 0
            self._set_reward_discount_for_lines(program)
        return res

    def _get_applied_programs_with_rewards_on_current_order(self):
        """
        Override method to ignore discount in line programs by context
        """
        programs = super()._get_applied_programs_with_rewards_on_current_order()
        if self.env.context.get("ignore_reward_type_with_discount_line"):
            programs = programs.filtered(
                lambda program: program.reward_type != "discount_line"
            )
        return programs
