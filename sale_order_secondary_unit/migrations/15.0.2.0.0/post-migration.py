# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set default sale secondary uom from template to variants
    sql = """
        UPDATE product_product pp
        SET sale_secondary_uom_id = pt.sale_secondary_uom_id
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
        AND pt.sale_secondary_uom_id IS NOT NULL
    """
    openupgrade.logged_query(env.cr, sql)
