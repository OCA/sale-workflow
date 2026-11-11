# Copyright 2026 Akretion (https://www.akretion.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    env.cr.execute(
        """
        UPDATE sale_order_line sol
        SET is_warehouse_id_following_order = (
            sol.warehouse_id IS NULL OR sol.warehouse_id = so.warehouse_id
        )
        FROM sale_order so
        WHERE so.id = sol.order_id
        """
    )
