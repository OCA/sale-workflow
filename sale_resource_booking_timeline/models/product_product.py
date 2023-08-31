from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_resource_booking(self):
        action = super().action_view_resource_booking()

        # Get the product's resource combinations to show on the left side of the timeline.
        combination_ids = [
            self.resource_booking_type_combination_rel_id.combination_id.id
        ]
        if combination_ids == [False]:
            combination_ids = self.resource_booking_type_id.combination_rel_ids.mapped(
                "combination_id"
            ).ids
        # Include "Show in timeline"
        action["domain"] = [
            "|",
            ("product_template_ids", "in", self.product_tmpl_id.id),
            ("combination_id", "in", combination_ids),
        ]

        return action
