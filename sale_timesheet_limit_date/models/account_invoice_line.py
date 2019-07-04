# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, values):
        # unlink lines from invoice if they under limit_date
        res = super().create(values)
        to_clean = self.env['account.analytic.line']
        for invoice_line in res:
            if (invoice_line.invoice_id.type == 'out_invoice'
                    and invoice_line.invoice_id.state == 'draft'
                    and invoice_line.invoice_id.timesheet_limit_date):
                sale_line_delivery = invoice_line.sale_line_ids.filtered(
                    lambda sol: sol.product_id.invoice_policy == 'delivery'
                    and sol.product_id.service_type == 'timesheet')
                if sale_line_delivery:
                    to_clean += self.env['account.analytic.line'].search([
                        ('timesheet_invoice_id', '=',
                            invoice_line.invoice_id.id),
                        ('date', '>',
                            invoice_line.invoice_id.timesheet_limit_date),
                    ])
        to_clean.write({'timesheet_invoice_id': False})
        return res
