# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Create discount columns in database")
    # Use IF NOT EXISTS to alter table because when the module is already
    # installed (v9.0 for example) and you migrate to this 13.0, the column
    # already exists but the module is considered as new.
    # So this hook is triggered and it raise an exception.
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS price_total_no_discount numeric;
    """
    )
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS discount_total numeric;
    """
    )
    cr.execute(
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS price_total_no_discount
        numeric;
    """
    )
    cr.execute(
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS discount_total numeric;
    """
    )


def post_init_hook(cr, registry):
    _logger.info("Compute discount columns")
    env = Environment(cr, SUPERUSER_ID, {})

    query = """
    update sale_order_line
    set price_total_no_discount = price_total
    where discount = 0.0
    """
    cr.execute(query)

    query = """
        update sale_order
        set price_total_no_discount = amount_total
        """
    cr.execute(query)

    query = """
    select distinct order_id from sale_order_line where discount > 0.0;
    """

    cr.execute(query)
    order_ids = cr.fetchall()

    orders = env["sale.order"].search([("id", "in", order_ids)])
    orders.mapped("order_line")._update_discount_display_fields()
