from odoo import _, fields, models


class SaleCouponReward(models.Model):
    """Extend to add discount_apply_on -> most_expensive_product opt."""

    _inherit = "sale.coupon.reward"

    discount_apply_on = fields.Selection(
        selection_add=[("most_expensive_product", "On Most Expensive Product")],
        help="On Order - Discount on whole order\n"
        "Cheapest product - Discount on cheapest product of the order\n"
        "Most Expensive product - Discount on most expensive product of the order\n"
        "Specific products - Discount on selected specific products",
    )

    def name_get(self):
        """Extend to update name for most_expensive_product option."""
        result = super().name_get()
        most_exp_names = {}
        for reward in self:
            if (
                reward.reward_type == "discount"
                and reward.discount_type == "percentage"
                and reward.discount_apply_on == "most_expensive_product"
            ):
                reward_percentage = str(reward.discount_percentage)
                most_exp_names[reward.id] = _(
                    "%s%% discount on most expensive product" % (reward_percentage)
                )
        if most_exp_names:
            result_dct = dict(result)
            result_dct.update(most_exp_names)
            return [(k, v) for k, v in result_dct.items()]
        return result
