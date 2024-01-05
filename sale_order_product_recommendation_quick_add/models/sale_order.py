# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def sale_order_recommendation_quick_add_action(self):
        so_recomendation_wiz = (
            self.env["sale.order.recommendation"]
            .with_context(active_id=self.id)
            .create({})
        )
        so_recomendation_wiz.generate_recommendations()
        so_recomendation_wiz.action_accept()
