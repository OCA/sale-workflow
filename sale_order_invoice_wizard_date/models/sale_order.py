# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)
        invoice_date = self.env.context.get("wizard_order_invoice_date", False)
        if invoice_date:
            moves.write(
                {
                    "invoice_date": invoice_date,
                }
            )
        return moves
