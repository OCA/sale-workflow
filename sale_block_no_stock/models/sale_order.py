# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """Check the stock of the products before confirming the sale order."""
        if self.env.context.get("skip_block_no_stock_check") and all(
            self.env.user in company.sale_line_block_allowed_groups.users
            for company in self.mapped("company_id")
        ):
            return super().action_confirm()

        for record in self:
            field_to_check = record.sudo().company_id.sale_line_field_block
            if not field_to_check:
                continue

            blocked_lines = self.env["sale.order.line"].browse()
            lines = record.order_line.filtered_domain(
                [("product_type", "=", "product")]
            )
            for line in lines:
                if line.product_uom_qty > line[field_to_check.name]:
                    blocked_lines |= line
            if blocked_lines:
                action = (
                    self.env.ref("sale_block_no_stock.sale_order_block_wizard_action")
                    .sudo()
                    .read()[0]
                )
                action["context"] = {
                    "default_sale_line_block_ids": [
                        (0, 0, {"sale_line_id": line.id}) for line in blocked_lines
                    ]
                }
                return action

        return super().action_confirm()
