# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_cancel(self):
        # The action_cancel method is called from the '_action_cancel' method
        # of the sale_order model in sale_stock. To avoid a hard cancel of the
        # pickings whatever the state of the picking process, the current addon
        # add into the context the 'orders_cancel_by_running_procurements' key to
        # instruct that in place of cancelling the picking, we'll run the proper
        # procurement rules to cancel the remaining qties to deliver.
        sale_order_ids = self.env.context.get("orders_cancel_by_running_procurements")
        if not sale_order_ids:
            return super().action_cancel()
        return (
            self.env["sale.order"]
            .browse(sale_order_ids)
            ._cancel_by_running_procurements()
        )
