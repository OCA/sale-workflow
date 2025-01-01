from openupgradelib import openupgrade

column_renames = {
    "account_payment_term": [
        ("default_delivery_block", "default_delivery_block_reason_id")
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, "account_payment_term", "default_delivery_block"
    ):
        openupgrade.rename_columns(env.cr, column_renames)
