# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _prepare_dict_account_payment(self, invoice):
        vals = super()._prepare_dict_account_payment(invoice)
        if invoice.payment_mode_id:
            payment_mode = invoice.payment_mode_id
            journal = payment_mode.fixed_journal_id
            method_line = journal.inbound_payment_method_line_ids.filtered(
                lambda l: l.payment_method_id == payment_mode.payment_method_id
            )[:1]
            vals["payment_type"] = payment_mode.payment_type
            vals["journal_id"] = journal.id
            vals.pop("payment_method_id", None)
        if method_line:
            vals["payment_method_line_id"] = method_line.id

            return vals


def _register_payment_invoice(self, invoice):
    if not invoice.payment_mode_id.fixed_journal_id:
        _logger.debug(
            "Unable to Register Payment for invoice %s: "
            "Payment mode %s must have fixed journal",
            invoice.id,
            invoice.payment_mode_id.id,
        )
        return
    return super()._register_payment_invoice(invoice)
