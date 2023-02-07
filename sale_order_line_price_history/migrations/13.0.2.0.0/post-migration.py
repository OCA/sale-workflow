# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line sol
        SET order_partner_id = so.partner_id
        FROM sale_order so
        WHERE so.id = sol.order_id AND sol.order_partner_id != so.partner_id
    """,
    )
