# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

# The module was renamed from sale_procurement_group_by_line to
# sale_stock_reference_by_line during the migration to 19.0, following the
# replacement of procurement.group by stock.reference in Odoo 19 core.
#
_renamed_fields = [
    (
        "sale.order.line",
        "sale_order_line",
        "procurement_group_id",
        "stock_reference_id",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _renamed_fields)
