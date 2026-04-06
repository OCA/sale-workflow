from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """Inherited the method allow order confirmation only if amount exceeds
        company minimum or user is Sales Manager."""
        # Allow confirmation if user is Sales Manager
        if self.env.user.has_group("sales_team.group_sale_manager"):
            return super().action_confirm()
        # Otherwise, validate each order amount
        for order in self:
            sale_min_order_limit = order.company_id.sale_min_order_limit
            if order.amount_untaxed <= sale_min_order_limit:
                raise UserError(
                    _(
                        "Only sale orders over %(amount).2f %(currency)s can be confirmed.",
                        amount=sale_min_order_limit,
                        currency=order.currency_id.symbol,
                    )
                )
        return super().action_confirm()
