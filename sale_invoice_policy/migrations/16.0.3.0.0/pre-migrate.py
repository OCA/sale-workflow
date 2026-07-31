from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # fill invoice_policy with values from default_invoice_policy, as invoice_policy
    # isn't anymore a store=False
    if openupgrade.column_exists(env.cr, "product_template", "default_invoice_policy"):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE product_template
            SET invoice_policy = default_invoice_policy
            WHERE default_invoice_policy IS NOT NULL
            """,
        )
