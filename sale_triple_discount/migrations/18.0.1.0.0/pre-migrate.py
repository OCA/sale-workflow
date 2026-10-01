# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


def migrate_discount_to_discount1(env):
    openupgrade.add_fields(
        env,
        [
            (
                "discount1",
                "sale.order.line",
                "sale_order_line",
                "float",
                "numeric",
                "sale_triple_discount",
                0.0,
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET discount1 = discount;
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET discount = 100 * (
            1 - (
                    (100 - COALESCE(discount1, 0.0)) / 100
                    * (100 - COALESCE(discount2, 0.0)) / 100
                    * (100 - COALESCE(discount3, 0.0)) / 100
                )
        )
        WHERE discounting_type='multiplicative';
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET discount = 100 * (
            1 - (
                    (100 - COALESCE(discount1, 0.0)) / 100
                    + (100 - COALESCE(discount2, 0.0)) / 100
                    + (100 - COALESCE(discount3, 0.0)) / 100
                )
        )
        WHERE discounting_type='additive';
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    migrate_discount_to_discount1(env)
