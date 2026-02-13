# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

RENAME_MAP = {
    "product_category": [
        ("manual_sale_min_qty", "sale_own_min_qty"),
        ("manual_sale_max_qty", "sale_own_max_qty"),
        ("manual_sale_multiple_qty", "sale_own_multiple_of_qty"),
    ],
    "product_template": [
        ("manual_sale_min_qty", "sale_own_min_qty"),
        ("manual_sale_max_qty", "sale_own_max_qty"),
        ("manual_sale_multiple_qty", "sale_own_multiple_of_qty"),
    ],
    "product_product": [
        ("manual_sale_min_qty", "sale_own_min_qty"),
        ("manual_sale_max_qty", "sale_own_max_qty"),
        ("manual_sale_multiple_qty", "sale_own_multiple_of_qty"),
    ],
}


def migrate_selection_and_flags(cr, table):
    """
    Map legacy 'manual_force_*' selections to new Blocking/Warning selections
    and set the new 'is_sale_own_*_set' flags.
    """
    for field in ["min_qty", "max_qty"]:
        old_col = f"manual_force_sale_{field}"
        new_col = f"sale_own_restrict_{field}"
        flag_col = f"is_sale_own_restrict_{field}_set"

        if openupgrade.column_exists(cr, table, old_col):
            # 1. Create the new columns if they don't exist yet
            # (Odoo usually creates them in post, but we need them for data move)
            if not openupgrade.column_exists(cr, table, new_col):
                cr.execute(
                    "ALTER TABLE %s ADD COLUMN %s varchar", (AsIs(table), AsIs(new_col))
                )
            if not openupgrade.column_exists(cr, table, flag_col):
                cr.execute(
                    "ALTER TABLE %s ADD COLUMN %s boolean DEFAULT false",
                    (AsIs(table), AsIs(flag_col)),
                )

            # 2. Map data
            # 'force' -> '1' (Blocking), is_set = True
            cr.execute(
                "UPDATE %s SET %s = '1', %s = True WHERE %s = 'force'",
                (AsIs(table), AsIs(new_col), AsIs(flag_col), AsIs(old_col)),
            )
            # 'not_force' -> '0' (Warning), is_set = True
            cr.execute(
                "UPDATE %s SET %s = '0', %s = True WHERE %s = 'not_force'",
                (AsIs(table), AsIs(new_col), AsIs(flag_col), AsIs(old_col)),
            )
            # 'use_parent' (or null) -> is_set = False
            cr.execute(
                "UPDATE %s SET %s = False WHERE %s = 'use_parent' OR %s IS NULL",
                (AsIs(table), AsIs(flag_col), AsIs(old_col), AsIs(old_col)),
            )

    # Handle is_sale_own_*_set for value fields
    for field in ["min_qty", "max_qty", "multiple_of_qty"]:
        flag_col = f"is_sale_own_{field}_set"

        # Multiple-of was renamed from manual_sale_multiple_qty
        if field == "multiple_of_qty":
            old_val_col = "manual_sale_multiple_qty"
        else:
            old_val_col = f"manual_sale_{field}"

        if openupgrade.column_exists(cr, table, old_val_col):
            if not openupgrade.column_exists(cr, table, flag_col):
                cr.execute(
                    "ALTER TABLE %s ADD COLUMN %s boolean DEFAULT false",
                    (AsIs(table), AsIs(flag_col)),
                )

            # If a manual value was set (> 0), mark it as 'own value set'
            cr.execute(
                "UPDATE %s SET %s = True WHERE %s > 0",
                (AsIs(table), AsIs(flag_col), AsIs(old_val_col)),
            )


@openupgrade.migrate()
def migrate(cr, version):
    # 1. Rename simple value columns
    openupgrade.rename_columns(cr, RENAME_MAP)

    # 2. Migrate selections and flags for each affected table
    for table in ["product_category", "product_template", "product_product"]:
        migrate_selection_and_flags(cr, table)
