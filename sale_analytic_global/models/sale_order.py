# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        help="This analytic distribution will be propagated to all lines "
        "analytic distributions, if you need to use different "
        "analytic distribution, define it at line level.",
    )

    @api.depends("order_line.analytic_distribution")
    def _compute_analytic_distribution(self):
        """Set the analytic distribution on the order based on its order lines.

        If all order lines have the same analytic distribution,
        then set it on the order, otherwise left the field empty.
        """
        res = super()._compute_analytic_distribution()
        for order in self:
            distributions = order.order_line.mapped("analytic_distribution")
            if distributions and all(
                distribute == distributions[0] for distribute in distributions
            ):
                order.analytic_distribution = distributions[0]
            else:
                order.analytic_distribution = False
        return res

    def _inverse_analytic_distribution(self):
        """Propagate the analytic distribution to order lines if set on the order"""
        for order in self:
            if order.analytic_distribution:
                order.order_line.analytic_distribution = order.analytic_distribution
