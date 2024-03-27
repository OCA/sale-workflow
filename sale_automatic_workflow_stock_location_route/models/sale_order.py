# Copyright 2024 Akretion (http://www.akretion.com/)
# @author: Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def automatic_set_route_on_sol(self):
        for sale in self:
            route_id = sale.workflow_process_id.sale_line_route_id
            if route_id:
                sale.order_line.filtered(
                    lambda sol: sol.qty_delivered_method == "stock_move"
                ).route_id = route_id

    def _action_confirm(self):
        self.automatic_set_route_on_sol()
        return super()._action_confirm()

    @api.onchange("workflow_process_id")
    def _onchange_workflow_process_id(self):
        """if there is a sale_line_route_id set in the workflow
        then wipe the existing route_id on order line to avoid
        a confusion for the user, as they can be modified at confirmation time"""
        res = super()._onchange_workflow_process_id()
        route_id = self.workflow_process_id.sale_line_route_id
        if route_id:
            self.order_line.filtered(
                lambda sol: sol.qty_delivered_method == "stock_move"
            ).route_id = False
        return res
