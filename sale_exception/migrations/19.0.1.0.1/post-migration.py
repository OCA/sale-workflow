from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env, "sale_exception", "migrations/19.0.1.0.1/noupdate_changes.xml"
    )
