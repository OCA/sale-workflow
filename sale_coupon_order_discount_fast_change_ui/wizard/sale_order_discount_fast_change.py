from odoo import fields, models


class SaleOrderDiscountFastChange(models.TransientModel):
    _inherit = "sale.order.discount.fast.change"

    skip_reward_lines = fields.Boolean(
        string="Skip reward lines",
        default=True,
    )

    def _get_lines_to_apply(self):
        so_lines = super()._get_lines_to_apply()
        if self.skip_reward_lines:
            # Get the sale order
            sale_order = self.env["sale.order"].browse(
                self.env.context.get("active_id")
            )
            # Remove non paid lines from the recordset
            so_lines &= sale_order._get_paid_order_lines()
        return so_lines
