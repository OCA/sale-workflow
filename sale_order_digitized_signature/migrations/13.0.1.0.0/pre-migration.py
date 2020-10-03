# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 OSI - Maxime Chambreuil
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {"sale.order": [("customer_signature", None)]}


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "sale_order", "customer_signature"):
        openupgrade.rename_columns(env.cr, column_renames)
