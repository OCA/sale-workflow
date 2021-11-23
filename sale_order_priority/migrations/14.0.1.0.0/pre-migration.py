# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    "sale_order": [
        ("priority", None, None),
    ],
    "sale_order_line": [
        ("priority", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    openupgrade.copy_columns(env.cr, _column_copies)
