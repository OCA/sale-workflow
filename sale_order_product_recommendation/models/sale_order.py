# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_sale_order_product_recommendation_wiz(self):
        recommendation_wiz = self.env["sale.order.recommendation"].search(
            [("order_id", "=", self.id)], limit=1
        )
        # Re-generate all so lines in recommendation lines
        recommendation_wiz.line_ids.filtered("sale_line_id").unlink()
        found_dict = {}
        existing_product_ids = set()
        recommendation_wiz.line_ids += (
            recommendation_wiz._fill_existing_sale_order_line(
                found_dict, existing_product_ids
            )
        )
        action = recommendation_wiz.get_formview_action()
        action["context"] = {"default_order_id": self.id}
        action["target"] = "new"
        return action


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Add database index to get last sale price query performance
    product_id = fields.Many2one(index=True)
