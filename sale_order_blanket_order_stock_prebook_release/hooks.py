# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Create `account.payment.method` records
    for the installed payment providers.
    """
    _logger.info(
        "Executing post init hook for module "
        "sale_order_blanket_order_stock_prebook_release"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    blanket_orders = env["sale.order"].search(
        [("order_type", "=", "blanket"), ("state", "in", ["sale", "done"])]
    )

    _logger.info(
        f"Found {len(blanket_orders)} blanket orders to compute the move date priority"
    )
    blanket_orders._compute_blanket_move_date_priority()

    _logger.info("Setting the move date priority for the blanket orders move lines")
    for move_id in blanket_orders.order_line.move_ids:
        if move_id.state not in ("done", "cancel", "assigned"):
            move_id.date_priority = (
                move_id.sale_line_id.order_id.blanket_move_date_priority
            )
