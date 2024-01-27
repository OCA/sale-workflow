# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def create_revision(self):
        # Extends base_revision module
        action = super().create_revision()
        # Keep links to Stock Moves on the new Sale Order
        old_so = self
        new_so = self.current_revision_id
        new_so.procurement_group_id.sale_id = old_so
        new_so.picking_ids = old_so.picking_ids
        for old_line, new_line in zip(old_so.order_line, new_so.order_line):
            new_line.move_ids = old_line.move_ids
        return action
