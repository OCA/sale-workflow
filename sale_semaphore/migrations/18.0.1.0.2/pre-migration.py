# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_column_renames = {
    "product_product": [
        ("semaphore_active", None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    field = env["ir.model.fields"].search(
        [("model", "=", "product.product"), ("name", "=", "semaphore_active")]
    )
    if field.ttype == "boolean":
        openupgrade.rename_columns(env.cr, _column_renames)
