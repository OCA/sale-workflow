# Copyright (C) 2021 Manuel Calero <manuelcalero@xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"
    _description = "Scheduler that will play automatically the send of invoices"

    def _do_send_invoice(self, invoice, domain_filter):
        """Send an invoice"""
        if not self.env["account.move"].search_count(
            [("id", "=", invoice.id)] + domain_filter
        ):
            return "{} {} job bypassed".format(invoice.display_name, invoice)
        template = self.env.ref(
            "account.email_template_edi_invoice", raise_if_not_found=False
        )
        invoice.message_post_with_template(
            template.id,
            composition_mode="comment",
            email_layout_xmlid="mail.mail_notification_paynow",
        )
        invoice.sudo().write({"invoice_sent": True})

    @api.model
    def _send_invoices(self, send_invoice_filter):
        move_obj = self.env["account.move"]
        invoices = move_obj.search(send_invoice_filter)
        _logger.debug("Invoices to send: %s", invoices.ids)
        for invoice in invoices:
            self._do_send_invoice(invoice, send_invoice_filter)

    @api.model
    def run_with_workflow(self, sale_workflow):
        super().run_with_workflow(sale_workflow)
        workflow_domain = [("workflow_process_id", "=", sale_workflow.id)]
        if sale_workflow.send_invoice:
            self._send_invoices(
                safe_eval(sale_workflow.send_invoice_filter_id.domain) + workflow_domain
            )
