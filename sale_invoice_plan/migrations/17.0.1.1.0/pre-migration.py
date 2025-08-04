# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "sale_order", "invoice_plan_pending"):
        openupgrade.add_columns(
            env, [("sale_order", "invoice_plan_pending", "integer")]
        )
        _logger.info("Create invoice_plan_pending column in sale_order table.")
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE sale_order so
            SET invoice_plan_pending = sub.count
            FROM (
                SELECT sale_id, COUNT(*) AS count
                FROM sale_invoice_plan
                WHERE NOT invoiced
                GROUP BY sale_id
            ) AS sub
            WHERE so.id = sub.sale_id;
            """,
        )
        _logger.info("Updated invoice_plan_pending for existing sale orders.")
