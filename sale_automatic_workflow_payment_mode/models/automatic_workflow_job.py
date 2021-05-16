# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.sale_automatic_workflow.models.automatic_workflow_job import savepoint

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    @api.model
    def run_with_workflow(self, sale_wkf):
        workflow_domain = [("workflow_process_id", "=", sale_wkf.id)]
        res = super().run_with_workflow(sale_wkf)
        if sale_wkf.register_payment:
            self._register_payments(
                safe_eval(sale_wkf.payment_filter_id.domain) + workflow_domain
            )
        return res

    @api.model
    def _register_payments(self, payment_filter):
        invoice_obj = self.env["account.move"]
        invoices = invoice_obj.search(payment_filter)
        _logger.debug("Invoices to Register Payment: %s", invoices.ids)

        domain = [
            ("account_internal_type", "in", ("receivable", "payable")),
            ("reconciled", "=", False),
        ]
        for invoice in invoices:
            partner_type = (
                invoice.move_type in ("out_invoice", "out_refund")
                and "customer"
                or "supplier"
            )
            payment_mode = invoice.payment_mode_id

            if not payment_mode.fixed_journal_id:
                _logger.debug(
                    "Unable to Register Payment for invoice %s: "
                    "Payment mode %s must have fixed journal",
                    invoice.id,
                    payment_mode.id,
                )
                continue

            with savepoint(self.env.cr):
                payment = self.env["account.payment"].create(
                    {
                        "amount": invoice.amount_residual,
                        "date": fields.Date.context_today(self),
                        "payment_reference": invoice.payment_reference or invoice.name,
                        "partner_id": invoice.partner_id.id,
                        "partner_type": partner_type,
                        "payment_type": payment_mode.payment_type,
                        "payment_method_id": payment_mode.payment_method_id.id,
                        "journal_id": payment_mode.fixed_journal_id.id,
                    }
                )
                payment.action_post()

            if payment.state != "posted":
                continue

            payment_lines = payment.line_ids.filtered_domain(domain)
            lines = invoice.line_ids
            for account in payment_lines.account_id:
                (payment_lines + lines).filtered_domain(
                    [("account_id", "=", account.id), ("reconciled", "=", False)]
                ).reconcile()
        return
