# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Databases coming from versions where this field was not company dependent
    # still have the old integer column, which can't be cast to the jsonb column of
    # the company dependent field. Its values live in ir.property and are converted
    # in the post-migration.
    env.cr.execute(
        """
        SELECT data_type FROM information_schema.columns
        WHERE table_name = 'res_partner' AND column_name = 'sale_type'
        """
    )
    row = env.cr.fetchone()
    if row and row[0] != "jsonb":
        openupgrade.rename_columns(env.cr, {"res_partner": [("sale_type", None)]})
