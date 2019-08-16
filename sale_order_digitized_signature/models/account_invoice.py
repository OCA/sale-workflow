# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    customer_signature = fields.Binary(
        string='Customer acceptance',
        attachment=True)

    @api.model
    def create(self, values):
        invoice = super(AccountInvoice, self).create(values)
        if invoice.customer_signature:
            values = {'customer_signature': invoice.customer_signature}
            invoice._track_signature(values, 'customer_signature')
        # Get SO signature
        if invoice.origin:
            so_id = self.env['sale.order'].search([('name',
                                                    '=',
                                                    invoice.origin)],
                                                    limit=1)
            if so_id.customer_signature:
                invoice.customer_signature = so_id.customer_signature
        return invoice

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(AccountInvoice, self).write(values)
