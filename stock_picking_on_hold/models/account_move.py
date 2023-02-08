# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_invoice_paid(self):
        res = super().action_invoice_paid()
        orders = self.mapped("invoice_line_ids.sale_line_ids.order_id")
        orders.auto_set_invoice_block()
        return res
