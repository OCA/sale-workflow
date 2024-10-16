import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Compute discount columns")
    env = Environment(cr, SUPERUSER_ID, {})

    query = """
    update sale_order_line
    set
        price_subtotal_no_discount = price_subtotal
    where discount = 0.0
    """
    cr.execute(query)

    query = """
    update sale_order
    set
        price_subtotal_no_discount = amount_untaxed
    """
    cr.execute(query)

    query = """
    select distinct order_id from sale_order_line where discount > 0.0;
    """

    cr.execute(query)
    order_ids = cr.fetchall()

    orders = env["sale.order"].search([("id", "in", order_ids)])
    orders.mapped("order_line")._update_discount_display_fields()
