import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = Environment(cr, SUPERUSER_ID, {})

    _logger.info("Compute discount columns sale_order_line.price_subtotal_no_discount")
    query = """
    UPDATE sale_order_line
    SET price_subtotal_no_discount = price_subtotal
    WHERE discount = 0.0
    """
    cr.execute(query)

    _logger.info("Compute discount columns sale_order.price_subtotal_no_discount")
    query = """
    UPDATE sale_order
    SET price_subtotal_no_discount = amount_untaxed
    """
    cr.execute(query)

    query = """
    select distinct order_id from sale_order_line where discount > 0.0;
    """

    cr.execute(query)
    order_ids = cr.fetchall()

    _logger.info("Search all orders with discounted lines...")
    orders = env["sale.order"].search([("id", "in", order_ids)])
    _logger.info(f"Found {len(orders)} orders.")
    for i, order in enumerate(orders, start=1):
        lines = order.mapped("order_line").filtered(lambda x: x.discount)
        _logger.info(f"{i} / {len(orders)}. order #{order.id} computing order lines data for {len(lines)} lines.")
        lines._compute_discount()
