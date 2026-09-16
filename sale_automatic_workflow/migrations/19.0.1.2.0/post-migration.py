# Copyright 2026 360ERP (https://www.360erp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# The payment filter lives in a noupdate="1" data file, so an existing
# database keeps the old domain on upgrade. Update it, but only when the
# user has not customised it, so we never silently overwrite someone's
# deliberate configuration.
OLD_DOMAIN = (
    "[('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), "
    "('payment_state','=','not_paid')]"
)
NEW_DOMAIN = (
    "[('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), "
    "('payment_state','=','not_paid'), ('amount_residual','!=',0)]"
)


def _normalize(domain):
    """Compare domains ignoring whitespace differences."""
    return "".join((domain or "").split())


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    payment_filter = env.ref(
        "sale_automatic_workflow.automatic_workflow_payment_filter",
        raise_if_not_found=False,
    )
    if not payment_filter:
        return
    if _normalize(payment_filter.domain) != _normalize(OLD_DOMAIN):
        _logger.info(
            "Automatic Workflow Payment Filter has been customised, "
            "leaving it untouched. Consider adding "
            "('amount_residual', '!=', 0) to it."
        )
        return
    payment_filter.domain = NEW_DOMAIN
    _logger.info(
        "Automatic Workflow Payment Filter updated to exclude invoices "
        "with a zero residual amount."
    )
