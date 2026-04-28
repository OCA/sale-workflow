from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env, "sale_planner_calendar", "migrations/18.0.1.0.0/noupdate_changes.xml"
    )
