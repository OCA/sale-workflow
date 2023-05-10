# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


def link_target_partner_id_to_recurrent_events(env):
    events = env["calendar.event"].search([("target_partner_id", "!=", False)])
    for event in events:
        to_assign_events = event.search(
            [
                ("target_partner_id", "=", False),
                ("recurrence_id", "=", event.recurrence_id.id),
            ]
        )
        to_assign_events.target_partner_id = event.target_partner_id


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "sale_planner_calendar", "migrations/15.0.1.0.1/noupdate_changes.xml"
    )
    link_target_partner_id_to_recurrent_events(env)
