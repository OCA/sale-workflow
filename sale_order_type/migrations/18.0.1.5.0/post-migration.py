# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tools.sql import column_exists


def migrate(cr, version):
    """Turn the old single analytic account into a full analytic distribution."""
    if not column_exists(cr, "sale_order_type", "analytic_account_id"):
        return
    cr.execute(
        """
        UPDATE sale_order_type
        SET analytic_distribution = jsonb_build_object(
            analytic_account_id::text, 100.0
        )
        WHERE analytic_account_id IS NOT NULL
        AND analytic_distribution IS NULL
        """
    )
