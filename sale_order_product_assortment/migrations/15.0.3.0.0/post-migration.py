from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "sale_order_product_assortment",
        "migrations/15.0.3.0.0/noupdate_changes.xml",
    )
