# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        """When an invoice is paid a picking that is hold until payment may need
        a status check"""
        res = super(AccountMove, self).write(vals)
        pickings_to_check = self.env["stock.picking"]
        for invoice in self.filtered(lambda i: i.state == "posted"):
            for sale in invoice.invoice_line_ids.mapped("sale_line_ids").mapped(
                "order_id"
            ):
                for picking in sale.picking_ids:
                    if picking.state == "hold":
                        pickings_to_check += picking
        # trigger availability check
        if pickings_to_check:
            pickings_to_check.action_assign_unpaid()
        return res

    def confirm_paid(self):
        """
        When an invoice is paid
        a picking that is hold until payment may need a status check.
        """
        res = super(AccountMove, self).confirm_paid()
        # collect all pickings to check
        pickings_to_check = self.env["stock.picking"]
        for invoice in self:
            for sale in invoice.sale_ids:
                for picking in sale.picking_ids:
                    if picking.state == "hold":
                        pickings_to_check += picking
        # trigger availability check
        pickings_to_check.action_assign()
        return res
