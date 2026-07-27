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
    """Map legacy restriction selections to the new Blocking/Warning selections
    and populate the new ``is_sale_own_*_set`` flags.

    This must run *before* :func:`openupgrade.rename_columns`, while the legacy
    ``manual_sale_*`` value columns are still present.

    Note: ``is_sale_own_restrict_*_qty_set`` fields are computed from
    ``bool(sale_own_restrict_*_qty)`` (not stored), so only the stored
    selection columns are populated here.
    """
    # 1. min_qty / max_qty carried an explicit force selection in the legacy
    #    version: force / not_force / use_parent.
    for field in ["min_qty", "max_qty"]:
        old_col = f"manual_force_sale_{field}"
        new_col = f"sale_own_restrict_{field}"

        if not openupgrade.column_exists(cr, table, old_col):
            continue
        if not openupgrade.column_exists(cr, table, new_col):
            cr.execute(
                "ALTER TABLE %s ADD COLUMN %s varchar", (AsIs(table), AsIs(new_col))
            )
        # 'force' -> '1' (Blocking)
        cr.execute(
            "UPDATE %s SET %s = '1' WHERE %s = 'force'",
            (AsIs(table), AsIs(new_col), AsIs(old_col)),
        )
        # 'not_force' -> '0' (Warning)
        cr.execute(
            "UPDATE %s SET %s = '0' WHERE %s = 'not_force'",
            (AsIs(table), AsIs(new_col), AsIs(old_col)),
        )
        # 'use_parent' (or NULL) leaves the new selection NULL, i.e. inherited.

    # 2. multiple_of_qty had NO force selection in the legacy version: the
    #    constraint was always enforced (Blocking) whenever a multiple value
    #    was set. Preserve that behaviour explicitly, otherwise a migrated
    #    multiple-of would silently degrade to a non-blocking warning.
    old_multiple_col = "manual_sale_multiple_qty"
    new_multiple_restrict_col = "sale_own_restrict_multiple_of_qty"
    if openupgrade.column_exists(cr, table, old_multiple_col):
        if not openupgrade.column_exists(cr, table, new_multiple_restrict_col):
            cr.execute(
                "ALTER TABLE %s ADD COLUMN %s varchar",
                (AsIs(table), AsIs(new_multiple_restrict_col)),
            )
        cr.execute(
            "UPDATE %s SET %s = '1' WHERE %s > 0",
            (AsIs(table), AsIs(new_multiple_restrict_col), AsIs(old_multiple_col)),
        )

    # 3. Populate the stored ``is_sale_own_<field>_set`` flags wherever a manual
    #    value was set (> 0) in the legacy columns.
    for field in ["min_qty", "max_qty", "multiple_of_qty"]:
        flag_col = f"is_sale_own_{field}_set"
        if field == "multiple_of_qty":
            old_val_col = "manual_sale_multiple_qty"
        else:
            old_val_col = f"manual_sale_{field}"

        if not openupgrade.column_exists(cr, table, old_val_col):
            continue
        if not openupgrade.column_exists(cr, table, flag_col):
            cr.execute(
                "ALTER TABLE %s ADD COLUMN %s boolean DEFAULT false",
                (AsIs(table), AsIs(flag_col)),
            )
        cr.execute(
            "UPDATE %s SET %s = True WHERE %s > 0",
            (AsIs(table), AsIs(flag_col), AsIs(old_val_col)),
        )


@openupgrade.migrate()
def migrate(env, version):
    # 1. Migrate selections and flags while the legacy 'manual_*' value columns
    #    are still present.
    cr = env.cr
    for table in ["product_category", "product_template", "product_product"]:
        migrate_selection_and_flags(cr, table)

    # 2. Rename the legacy value columns to their new names.
    openupgrade.rename_columns(cr, RENAME_MAP)
