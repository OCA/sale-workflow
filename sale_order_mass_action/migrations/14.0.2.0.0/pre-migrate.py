# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_selection_field(env):
    action_field = [
        (
            "action",
            "sale.order.mass.action.wizard",
            "sale_order_mass_action_wizard",
            "selection",
            "varchar",
            "sale_order_mass_action",
        )
    ]
    openupgrade.add_fields(env, action_field)
    query = """
        UPDATE sale_order_mass_action_wizard
            SET action = 'confirm'
            WHERE confirm = True
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_selection_field(env)
