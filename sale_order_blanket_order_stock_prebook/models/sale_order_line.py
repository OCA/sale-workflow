# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _launch_stock_rule_on_blanket_order(self, previous_product_uom_qty):
        other_lines = self.browse()
        for line in self:
            line = line.with_context(call_off_sale_line_id=line.id)
            blanket_order = line.order_id.blanket_order_id
            if blanket_order.blanket_reservation_strategy == "at_confirm":
                line._stock_rule_on_blanket_with_reservation_at_confirm(
                    previous_product_uom_qty
                )
            else:
                other_lines |= line
        return super(SaleOrderLine, other_lines)._launch_stock_rule_on_blanket_order(
            previous_product_uom_qty
        )

    def _release_reservation(self):
        """Release the reservation of the stock for the order."""
        self.move_ids.filtered(lambda m: m.used_for_sale_reservation)._action_cancel()

    def _prepare_reserve_procurements(self, group):
        procurements = super()._prepare_reserve_procurements(group)
        forced_qty = self.env.context.get("force_qty")
        if forced_qty:
            self.ensure_one()
            proc = procurements[0]
            proc = self.env["procurement.group"].Procurement(
                proc.product_id,
                forced_qty,
                proc.product_uom,
                proc.location_id,
                proc.name,
                proc.origin,
                proc.company_id,
                values=proc.values,
            )
            procurements = [proc]
        return procurements

    def _prebook_stock(self, qty):
        """Prebook the stock for the order."""
        self = self.with_context(sale_stock_prebook_stop_proc_run=True)
        procurements = []
        for line in self:
            group = line.order_id._create_reserve_procurement_group()
            procurements += line.with_context(
                force_qty=qty
            )._prepare_reserve_procurements(group)
        if procurements:
            self.env["procurement.group"].run(procurements)
        return procurements

    def _stock_rule_on_blanket_with_reservation_at_confirm(
        self, previous_product_uom_qty
    ):
        self.ensure_one()
        blanket_line = self.blanket_line_id
        blanket_line._release_reservation()
        # Create a new reservation for the remaining quantity on the blanket order
        # Since the call_off_remaining qty is computed from the qty consumed by
        # the call off order and the current line is part of this qty, it
        # represents the real remaining qty to consume and therefore the qty to
        # reserve on the blanket order.
        remaining_qty = blanket_line.call_off_remaining_qty
        if (
            float_compare(
                remaining_qty, 0, precision_rounding=self.product_uom.rounding
            )
            > 0
        ):
            blanket_line._prebook_stock(remaining_qty)

        # run normal delivery rule on the blanket order. This will create the
        # move on the call off order for the qty not reserved IOW the qty to
        # deliver.
        old_state = blanket_line.state
        if old_state == "done":
            # Auto done -> set to confirmed to allow the stock rule to run
            blanket_line.state = "sale"
        blanket_line.with_context(
            disable_call_off_stock_rule=True
        )._action_launch_stock_rule(previous_product_uom_qty)
        if old_state == "done":
            # Restore the state
            blanket_line.state = "done"
