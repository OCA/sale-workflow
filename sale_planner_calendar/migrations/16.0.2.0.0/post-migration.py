# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def _sale_planner_calendar_event_to_calendar_event(env):
    """Move all data from sale_planner_calendar_event to code model calendar_event"""
    sql = """
        UPDATE calendar_event SET
            sale_planner_state = spce.state,
            calendar_issue_type_id = spce.calendar_issue_type_id,
            calendar_event_profile_id = spce.calendar_event_profile_id,
            comment = spce.comment,
            calendar_summary_id = spce.calendar_summary_id,
            off_planning = spce.off_planning
        FROM sale_planner_calendar_event spce
        WHERE spce.calendar_event_id = calendar_event.id
    """
    openupgrade.logged_query(env.cr, sql)


def _sale_order_to_calendar_event(env):
    """Link sale order to calendar events instead of sale planner calendar event model"""
    # drop_constraint(env.cr, 'sale_order', 'sale_order_sale_planner_calendar_event_id_fkey')
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order SET
            sale_planner_calendar_event_id = spce.calendar_event_id
        FROM sale_planner_calendar_event spce
        WHERE sale_order.%(old_column)s = spce.id
    """,
        {
            "old_column": AsIs(
                openupgrade.get_legacy_name("sale_planner_calendar_event_id")
            )
        },
    )


def _payment_sheet_to_calendar_event(env):
    """Link sale payment sheet to calendar events instead of sale planner calendar
    event model
    """
    # drop_constraint(env.cr, 'sale_payment_sheet_line',
    #                 'sale_payment_sheet_line_sale_planner_calendar_event_id_fkey')
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_payment_sheet_line SET
            sale_planner_calendar_event_id = spce.calendar_event_id
        FROM sale_planner_calendar_event spce
        WHERE sale_payment_sheet_line.%(old_column)s = spce.id
    """,
        {
            "old_column": AsIs(
                openupgrade.get_legacy_name("sale_planner_calendar_event_id")
            )
        },
    )


def _remove_selection_field_values(env):
    sql = """
        DELETE FROM ir_model_fields_selection
        WHERE field_id IN
            (SELECT id
                FROM ir_model_fields
                WHERE ttype='selection' AND model='sale.planner.calendar.event')
    """
    openupgrade.logged_query(env.cr, sql)


@openupgrade.migrate()
def migrate(env, version):
    _sale_planner_calendar_event_to_calendar_event(env)
    _sale_order_to_calendar_event(env)
    _payment_sheet_to_calendar_event(env)
    # _remove_selection_field_values(env)
