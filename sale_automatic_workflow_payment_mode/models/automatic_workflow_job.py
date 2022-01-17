# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _prepare_dict_account_payment(self, invoice):
        values = super()._prepare_dict_account_payment(invoice)
        payment_mode = invoice.payment_mode_id
        values.update(
            {
                "payment_reference": invoice.payment_reference or invoice.name,
                "payment_method_id": payment_mode.payment_method_id.id,
                "journal_id": payment_mode.fixed_journal_id.id,
            }
        )
        return values

    def _register_payment_invoice(self, invoice):
        payment_mode = invoice.payment_mode_id

        if not payment_mode.fixed_journal_id:
            _logger.debug(
                "Unable to Register Payment for invoice %s: "
                "Payment mode %s must have fixed journal",
                invoice.id,
                payment_mode.id,
            )
            return

        return super()._register_payment_invoice(invoice)
