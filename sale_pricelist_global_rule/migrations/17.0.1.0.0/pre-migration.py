# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_pricelist_item
            SET applied_on='3_1_global_product_template'
            WHERE applied_on = '4_global_product_template'
            """,
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_pricelist_item
            SET applied_on='3_2_global_product_category'
            WHERE applied_on = '5_global_product_category'
            """,
    )
