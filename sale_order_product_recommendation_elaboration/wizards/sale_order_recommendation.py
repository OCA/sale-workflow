# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class SaleOrderRecommendation(models.TransientModel):
    _inherit = "sale.order.recommendation"

    def generate_recommendations(self):
        # Let's prefetch all the values we need once and leave them in the context
        # so we can just gather them from cache.
        prefetched_lines = (
            self.env["sale.order.line"]
            .sudo()
            .search_fetch(
                self._recommendable_sale_order_lines_domain(),
                ["product_id", "date_order", "elaboration_ids", "elaboration_note"],
            )
        )
        return super(
            SaleOrderRecommendation,
            self.with_context(prefetched_lines=prefetched_lines),
        ).generate_recommendations()

    def _prepare_recommendation_line_vals(self, group_line, so_line=False):
        """Include elaboration info from last sales."""
        vals = super()._prepare_recommendation_line_vals(group_line, so_line)
        # Keep elaborations from the original line
        if so_line:
            vals.update(
                {
                    "elaboration_ids": [
                        fields.Command.set(so_line.elaboration_ids.ids)
                    ],
                    "elaboration_note": so_line.elaboration_note,
                }
            )
            return vals
        # Recommend last elaborations used
        product, *_ = group_line
        all_lines = self.env.context.get("prefetched_lines")
        last_line = all_lines.filtered(
            lambda x, product=product: x.product_id == product
        ).sorted(lambda x: x.date_order)[-1:]
        vals.update(
            {
                "elaboration_ids": [fields.Command.set(last_line.elaboration_ids.ids)],
                "elaboration_note": last_line.elaboration_note,
            }
        )
        return vals


class SaleOrderRecommendationLine(models.TransientModel):
    _name = "sale.order.recommendation.line"
    _inherit = ["sale.order.recommendation.line", "product.elaboration.mixin"]

    def _prepare_new_so_line_vals(self, sequence):
        """Transfer elaborations to a new sale order line."""
        res = super()._prepare_new_so_line_vals(sequence)
        res.update(
            {
                "elaboration_ids": [fields.Command.set(self.elaboration_ids.ids)],
                "elaboration_note": self.elaboration_note,
            }
        )
        return res

    def _prepare_update_so_line_vals(self):
        """Transfer elaborations to an existing sale order line."""
        res = super()._prepare_update_so_line_vals()
        res.update(
            {
                "elaboration_ids": [fields.Command.set(self.elaboration_ids.ids)],
                "elaboration_note": self.elaboration_note,
            }
        )
        return res
