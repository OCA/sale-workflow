# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    semaphore_legacy_column = openupgrade.get_legacy_name("semaphore_active")
    if not openupgrade.column_exists(
        env.cr, "product_product", semaphore_legacy_column
    ):
        return
    openupgrade.logged_query(
        env.cr,
        f"""
    UPDATE product_product pp
    SET semaphore_active = 'yes'
    WHERE COALESCE(pp.{semaphore_legacy_column}, false) = false
    """,
    )
