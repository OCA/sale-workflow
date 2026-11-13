# Copyright 2026 Komit-consulting - Duc Truong
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

GLOBAL_VALUES = (
    "3_1_global_product_template",
    "3_2_global_product_category",
)


@openupgrade.migrate()
def migrate(env, version):
    """Move the global rules from the old ``applied_on`` values to the new model.

    Before 18.0 the global rules were stored in ``applied_on`` with the values
    ``3_1_global_product_template`` and ``3_2_global_product_category``. Since 18.0
    they are ``applied_on = '3_global'`` (core value), ``display_applied_on =
    '3_global'`` and the kind of rule is kept in ``global_applied_on``.

    This must run in pre-migration: the old selection values are removed from
    ``applied_on`` when the module is updated (``set default``), after which the
    global rules can no longer be told apart from the standard ones.
    ``global_applied_on`` is a new field, so its column does not exist yet.
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE product_pricelist_item
        ADD COLUMN IF NOT EXISTS global_applied_on VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_pricelist_item
        SET global_applied_on = applied_on,
            display_applied_on = '3_global',
            applied_on = '3_global'
        WHERE applied_on IN %s
        """,
        (GLOBAL_VALUES,),
    )
