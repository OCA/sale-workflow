# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def action_invoice_sent(self):
        res = super().action_invoice_sent()
        sale_orders = self.invoice_line_ids.sale_line_ids.mapped("order_id")
        if not sale_orders:
            return res
        res["context"][
            "sale_order_attachments"
        ] = sale_orders._get_sale_document_attachments().ids
        return res
