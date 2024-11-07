# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceSend(models.TransientModel):

    _inherit = "account.invoice.send"

    @api.onchange("template_id")
    def onchange_template_id(self):
        res = super().onchange_template_id()
        if self.env.context.get("sale_order_attachments"):
            attachment_ids = self.attachment_ids.ids + self.env.context.get(
                "sale_order_attachments"
            )
            attachments = self.env["ir.attachment"].browse(attachment_ids)
            self.attachment_ids = attachments
        return res
