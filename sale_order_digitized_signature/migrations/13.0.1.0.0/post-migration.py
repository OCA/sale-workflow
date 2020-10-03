# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 OSI - Maxime Chambreuil
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade, openupgrade_90


@openupgrade.migrate()
def migrate(env, version):
    column = openupgrade.get_legacy_name("customer_signature")
    if openupgrade.column_exists(env.cr, "sale_order", column):
        openupgrade_90.convert_binary_field_to_attachment(
            env, {"sale.order": [("customer_signature", None)]}
        )
