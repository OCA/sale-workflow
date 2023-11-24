from odoo import fields, models

# TODO: Add more policies:
#   - A customizable application domain
#   - A discount threshold


class SaleOrderDiscountFastChange(models.TransientModel):
    _name = "sale.order.discount.fast.change"
    _description = "Sales Order Discount Fast Change"

    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)
    application_policy = fields.Selection(
        [
            ("not_discounted", "Apply only on not discounted lines"),
            ("all", "Apply on all lines"),
        ],
        string="Discount Application Policy",
        default="not_discounted",
        required=True,
    )

    def _get_not_discounted_lines_to_apply(self, sale_order):
        return sale_order.order_line.filtered(lambda sol: not sol.discount)

    def _get_lines_to_apply(self):
        sale_order = self.env["sale.order"].browse(self.env.context.get("active_id"))
        if self.application_policy == "not_discounted":
            so_lines = self._get_not_discounted_lines_to_apply(sale_order)
        else:
            so_lines = sale_order.order_line
        return so_lines

    def apply_global_discount(self):
        """
        Apply the entered discount to the selected lines depending
        on the application policy.
        """
        self._get_lines_to_apply().write({"discount": self.discount})
