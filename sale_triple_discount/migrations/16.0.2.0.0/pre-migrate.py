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
    # if discounts are : 10% - 20% - 30% main discount is : 49.6 %
    # if discounts are : 05% - 09% - 13% main discount is : 24.7885 %
    if "discount_fixed" not in env.registry.models["sale.order.line"]._fields:
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
            );
            """,
        )
    else:
        # don't touch lines with fixed discount
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
            WHERE discount_fixed = 0;
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    migrate_discount_to_discount1(env)
