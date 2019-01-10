# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order
        SET validity_date = date_validity
        WHERE date_validity IS NOT NULL
        """
    )
