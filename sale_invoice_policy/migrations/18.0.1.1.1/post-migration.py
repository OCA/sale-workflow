import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    sale_obj = env["sale.order"]
    so_without_invoice_policy = sale_obj.with_context(active_test=False).search(
        [("invoice_policy", "=", False)]
    )
    if so_without_invoice_policy:
        _logger.info(
            f"Recompute invoice_policy for # {len(so_without_invoice_policy)} "
            f"sale orders as is now required"
        )
        so_without_invoice_policy._compute_invoice_policy()
