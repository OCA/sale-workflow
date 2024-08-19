# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def create_revision(self):
        # Extends base_revision module
        action = super().create_revision()
        # Keep links to Invoices on the new Sale Order
        old_lines = self.order_line
        new_lines = self.current_revision_id.order_line
        for old_line, new_line in zip(old_lines, new_lines):
            new_line.invoice_lines = old_line.invoice_lines
        return action

    def action_cancel_create_revision(self):
        # Button to create new revison
        # Cancels the original order before creating the new revision
        for sale in self:
            sale.action_cancel()
            action = sale.create_revision()
        if len(self) == 1:
            return action
        return {}
