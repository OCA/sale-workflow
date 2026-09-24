# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    if openupgrade.is_module_installed(cr, "sale_warehouse_rule"):
        renamed_modules = [
            (
                "sale_warehouse_rule",
                "sale_sourced_by_line_product_rule",
            ),
        ]
        renamed_models = {
            "sale.warehouse.rule": "sale.line.product.rule",
        }
        renamed_tables = {
            "sale_warehouse_rule": "sale_line_product_rule",
        }
        openupgrade.rename_tables(cr, renamed_tables)
        openupgrade.rename_models(cr, renamed_models)
        openupgrade.update_module_names(cr, renamed_modules, merge_modules=False)
