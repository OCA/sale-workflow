# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET sale_type_id = ai.sale_type_id
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id""",
    )
    openupgrade.load_data(
        env.cr, "sale_order_type", "migrations/13.0.1.0.0/noupdate_changes.xml"
    )
