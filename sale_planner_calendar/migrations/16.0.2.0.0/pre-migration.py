# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    "sale_order": [
        ("sale_planner_calendar_event_id", None),
    ],
    "sale_payment_sheet_line": [("sale_planner_calendar_event_id", None)],
}


def _remove_selection_field_values(env):
    sql = """
        DELETE FROM ir_model_fields_selection
        WHERE field_id IN
            (SELECT id
                FROM ir_model_fields
                WHERE ttype='selection' AND model='sale.planner.calendar.event')
    """
    openupgrade.logged_query(env.cr, sql)


def _add_event_profile_helper_column(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE calendar_event_type
        ADD COLUMN old_sale_planner_profile_id integer""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    _remove_selection_field_values(env)
    _add_event_profile_helper_column(env)
