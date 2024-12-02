# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.tools import sql

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Create table columns for computed fields to not get them computed by Odoo.

    This is done to avoid MemoryError when installing the module on big databases.
    Also it is useless to compute these fields which should be empty when installing
    the module because no SO lines have a customer reference set.
    """
    # Create columns
    cr = env.cr
    if not sql.column_exists(cr, "stock_move", "customer_ref_sale_line_id"):
        sql.create_column(
            cr,
            "stock_move",
            "customer_ref_sale_line_id",
            "int4",
            comment="Sale Line With Customer Ref",
        )
    if not sql.column_exists(cr, "stock_move", "customer_ref"):
        sql.create_column(
            cr,
            "stock_move",
            "customer_ref",
            "VARCHAR",
        )
