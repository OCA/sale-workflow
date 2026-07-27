# Copyright 2026 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

# The restriction selection values changed from opaque "1"/"0" to the
# self-documenting "blocking"/"warning" for readability.
VALUE_MAP = {
    "1": "blocking",
    "0": "warning",
}

# All stored Selection columns that hold a restriction value (own, inherited
# and effective) for each restricted quantity.
RESTRICT_COLUMNS = [
    "sale_own_restrict_min_qty",
    "sale_inherited_restrict_min_qty",
    "sale_restrict_min_qty",
    "sale_own_restrict_max_qty",
    "sale_inherited_restrict_max_qty",
    "sale_restrict_max_qty",
    "sale_own_restrict_multiple_of_qty",
    "sale_inherited_restrict_multiple_of_qty",
    "sale_restrict_multiple_of_qty",
]

TABLES = ["product_category", "product_template", "product_product"]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    for table in TABLES:
        for column in RESTRICT_COLUMNS:
            if not openupgrade.column_exists(cr, table, column):
                continue
            for old_value, new_value in VALUE_MAP.items():
                cr.execute(
                    "UPDATE %s SET %s = %s WHERE %s = %s",
                    (AsIs(table), AsIs(column), new_value, AsIs(column), old_value),
                )
