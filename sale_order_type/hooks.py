import logging

from odoo.api import SUPERUSER_ID, Environment

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    Environment(cr, SUPERUSER_ID, {})
    logger.info("Add type_id field in sale_order table")
    cr.execute("ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS type_id INTEGER")


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    order_type = env["sale.order"]._default_type_id()
    if order_type:
        cr.execute(
            "UPDATE sale_order set type_id = %s where type_id is null", (order_type.id,)
        )
