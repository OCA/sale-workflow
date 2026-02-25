# Copyright 2024 Camptocamp SA
# Copyright 2026 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo.tools import column_exists

USE_OPENUPGRADE = False
USE_ODOOUPGRADE = False

try:
    from odoo.upgrade import util

    USE_ODOOUPGRADE = True
except ImportError:
    try:
        from openupgradelib import openupgrade

        USE_OPENUPGRADE = True
    except ImportError as err:
        raise ImportError(
            "This migration script requires openupgradelib or odoo.upgrade.util.\n"
            "Please install one of these libraries to proceed with the migration.\n"
            "For better performances, it is recommended to use odoo.upgrade.util.\n"
            "See https://github.com/odoo/upgrade-util/"
        ) from err


_logger = logging.getLogger(__name__)


def migrate_discount_to_discount1(cr):
    if not column_exists(cr, "sale_order_line", "discount1"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
            ADD COLUMN discount1 numeric;
            """
        )
        _logger.info("Added column 'discount1' to 'sale_order_line'")

    query = """
        UPDATE sale_order_line
        SET discount1 = discount,
         discount =
        CASE
            WHEN discounting_type = 'multiplicative' THEN 100 * (
                1 - (
                        (100 - COALESCE(discount, 0.0)) / 100
                        * (100 - COALESCE(discount2, 0.0)) / 100
                        * (100 - COALESCE(discount3, 0.0)) / 100
                    )
            )
            ELSE COALESCE(discount, 0.0) + COALESCE(discount2, 0.0) + COALESCE(discount3, 0.0)
        END
        """
    if USE_OPENUPGRADE:
        openupgrade.logged_query(
            cr,
            query,
        )
    else:
        util.parallel_execute(
            cr, util.explode_query_range(cr, query, table="sale_order_line")
        )


def migrate(cr, version):
    migrate_discount_to_discount1(cr)
