# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # OpenUpgrade's sale_stock only links each order to its
    # procurement_group_id, which is the last group this module created.
    # Orders with several groups (e.g. split per warehouse by
    # sale_sourced_by_line) would lose the link to their other references.
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO stock_reference_sale_rel (sale_id, reference_id)
        SELECT DISTINCT order_id, stock_reference_id
        FROM sale_order_line
        WHERE stock_reference_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """,
    )
