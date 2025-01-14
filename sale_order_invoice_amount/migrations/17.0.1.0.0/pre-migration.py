# Copyright 2025 ForgeFlow SL
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade

_field_renames = [
    (
        "sale.order",
        "sale_order",
        "invoiced_amount",
        "amount_invoiced",
    ),
    (
        "sale.order",
        "sale_order",
        "uninvoiced_amount",
        "amount_to_invoice",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    # Se utiliza un bucle para procesar cada par de campos
    for _, table, old_field, new_field in _field_renames:
        # Se verifica si los campos ya han sido procesados para evitar errores
        if openupgrade.column_exists(
            cr, table, old_field
        ) and openupgrade.column_exists(cr, table, new_field):
            openupgrade.logged_query(
                cr,
                f"""
                UPDATE {openupgrade.AsIs(table)}
                SET {openupgrade.AsIs(new_field)} = {openupgrade.AsIs(old_field)}
                """,
            )
            openupgrade.drop_columns(cr, [(table, old_field)])
