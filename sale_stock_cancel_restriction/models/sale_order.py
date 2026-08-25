# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        # Force to call the cancel method on done picking for having the
        # expected error, as Odoo has now filter out such pickings from the
        # cancel operation.
        domain = [("state", "=", "done")]
        if self.warehouse_id.restrict_sale_cancel_after_delivery:
            domain += [("picking_type_id.code", "=", "outgoing")]
        self.picking_ids.filtered_domain(domain).action_cancel()
        return super().action_cancel()
