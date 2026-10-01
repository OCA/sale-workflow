# Copyright 2025 Komit-consuting - DucTruongKomit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE product_pricelist_item
            SET display_applied_on = '3_global'
            WHERE applied_on IN (
                '3_1_global_product_template',
                '3_2_global_product_category',
                '3_3_global_product_ancestor_category'
            )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
             UPDATE product_pricelist_item
             SET global_applied_on = applied_on
             WHERE applied_on IN (
             '3_1_global_product_template',
             '3_2_global_product_category',
             '3_3_global_product_ancestor_category'
         )
        """,
    )
