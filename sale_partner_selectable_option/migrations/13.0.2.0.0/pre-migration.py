# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

field_renames = [
    ("res.partner", "res_partner", "selectable_in_sales_orders", "sale_selectable"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env.cr, field_renames)
