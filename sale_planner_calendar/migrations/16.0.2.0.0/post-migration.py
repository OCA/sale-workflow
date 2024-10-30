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


def _profiles_to_calendar_event_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO calendar_event_type (name, icon, old_sale_planner_profile_id)
            SELECT name, icon, id FROM sale_planner_calendar_event_profile
    """,
    )

    # Update event linked to profiles
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO meeting_category_rel (event_id, type_id)
            SELECT ce.id, cet.id
            FROM calendar_event ce
                JOIN calendar_event_type cet
                    ON cet.old_sale_planner_profile_id = ce.calendar_event_profile_id
    """,
    )


def _remove_renamed_selection_values(env):
    """After rename value from upper to lower the values are duplicated.
    This method removes old upper values"""
    week_list_field = env.ref(
        "sale_planner_calendar.field_sale_planner_calendar_wizard__week_list"
    )
    value_ids = week_list_field.selection_ids.filtered(lambda x: x.value.isupper()).ids
    if value_ids:
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM ir_model_fields_selection
            WHERE id in %(selection_value_ids)s
            """,
            {"selection_value_ids": tuple(value_ids)},
        )


@openupgrade.migrate()
def migrate(env, version):
    _sale_planner_calendar_event_to_calendar_event(env)
    _sale_order_to_calendar_event(env)
    _payment_sheet_to_calendar_event(env)
    _profiles_to_calendar_event_type(env)
    _remove_renamed_selection_values(env)
