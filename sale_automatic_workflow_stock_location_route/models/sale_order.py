# Copyright 2024 Akretion (http://www.akretion.com/)
# @author: Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_sols_to_automatically_set_route_on(self):
        self.ensure_one()
        route_policy = self.workflow_process_id.sale_line_route_policy
        return self.order_line.filtered(
            lambda sol: sol.qty_delivered_method == "stock_move"
            and (route_policy == "replace" or not sol.route_id)
        )

    def automatic_set_route_on_sol(self):
        for sale in self:
            route_id = sale.workflow_process_id.sale_line_route_id
            if route_id:
                sale._get_sols_to_automatically_set_route_on().route_id = route_id

    def _action_confirm(self):
        self.automatic_set_route_on_sol()
        return super()._action_confirm()

    @api.onchange("workflow_process_id")
    def _onchange_workflow_process_id(self):
        """Apply workflow route to sale order lines when workflow has a route defined.

        When switching to a workflow that has a route defined, this immediately
        applies the route to eligible lines based on the route policy to give
        users immediate visual feedback of what will happen at confirmation.
        """
        res = super()._onchange_workflow_process_id()
        self.automatic_set_route_on_sol()
        return res
