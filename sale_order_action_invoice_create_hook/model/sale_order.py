# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_invoice_group_key(self, order):
        return (order.partner_invoice_id.id, order.currency_id.id)

    @api.model
    def _get_invoice_group_line_key(self, line):
        return self._get_invoice_group_key(line.order_id)

    @api.model
    def _get_draft_invoices(self, invoices, references):
        return invoices, references


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice(self):
        return self.order_id._prepare_invoice()

    def _do_not_invoice(self):
        return False
