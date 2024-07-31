# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def action_download_attachment(self, attachment_ids):
        url = "/web/binary/download_document?tab_id=%s" % attachment_ids
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )
        order.attach_expense_receipt_to_invoice(invoice)
        return invoice
