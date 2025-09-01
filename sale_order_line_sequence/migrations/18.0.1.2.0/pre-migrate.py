from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE sale_order_line ALTER COLUMN visible_sequence TYPE varchar",
    )
