# # Copyright 2021 ForgeFlow S.L. (https://forgeflow.com)
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def change_priorities(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("priority"),
        "priority",
        [("1", "0"), ("2", "1"), ("3", "1")],
        table="sale_order",
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("priority"),
        "priority",
        [("1", "0"), ("2", "1"), ("3", "1")],
        table="sale_order_line",
    )


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    if not openupgrade.column_exists(
        env.cr, "sale_order", "priority"
    ) or not openupgrade.column_exists(env.cr, "sale_order_line", "priority"):
        return
    change_priorities(env)
