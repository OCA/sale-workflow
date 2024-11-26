# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    blanket_reservation_strategy = fields.Selection(
        selection_add=[("at_confirm", "At Order Confirmation")],
        ondelete={"at_confirm": "cascade"},
    )

    def _blanket_order_reserve_stock(self):
        """Reserve the stock for the blanket order."""
        other_orders = self.browse()
        to_reserve_at_confirm = self.browse()
        for order in self:
            if order.blanket_reservation_strategy == "at_confirm":
                to_reserve_at_confirm |= order
            else:
                other_orders |= order
        to_reserve_at_confirm._prebook_stock()
        return super(SaleOrder, other_orders)._blanket_order_reserve_stock()

    def _prebook_stock(self):
        """Prebook the stock for the order."""
        self = self.with_context(sale_stock_prebook_stop_proc_run=True)
        procurements = []
        for order in self:
            group = order._create_reserve_procurement_group()
            procurements += order.order_line._prepare_reserve_procurements(group)
        if procurements:
            self.env["procurement.group"].run(procurements)
