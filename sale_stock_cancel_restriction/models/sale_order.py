# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        self = self.with_context(disable_cancel_warning=True)
        # Force to call the cancel method on done picking for having the
        # expected error, as Odoo has now filter out such pickings from the
        # cancel operation.
        domain = [("state", "=", "done")]
        if self.warehouse_id.restrict_sale_cancel_after_delivery:
            domain += [("picking_type_id.code", "=", "outgoing")]
        self.picking_ids.filtered_domain(domain).action_cancel()
        return super(SaleOrder, self).action_cancel()

    def _show_cancel_wizard(self):
        res = super(SaleOrder, self)._show_cancel_wizard()
        for order in self:
            if any(
                picking.state == "done" for picking in order.picking_ids
            ) and not order._context.get("disable_cancel_warning"):
                return True
        return res
