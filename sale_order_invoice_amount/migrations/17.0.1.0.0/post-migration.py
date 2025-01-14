# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

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


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "Set 'enable_amount_invoiced_based_on_quantity to True "
        "so the amount to invoice is calculated based on quantity"
    )
    companies = env["res.company"].search([])
    companies.write({"enable_amount_invoiced_based_on_quantity": True})

    for model, table, old_field, new_field in _field_renames:
        if not openupgrade.column_exists(cr, table, old_field):
            # Update ir.model.data (if they exist)
            openupgrade.logged_query(
                cr,
                f"""
                UPDATE ir_model_data
                SET name = regexp_replace(name, '{old_field}', '{new_field}')
                WHERE module = 'sale_order_invoice_amount'
                AND name ~ '{".*" + old_field + ".*"}'
                """,
            )
            # Update translations
            openupgrade.logged_query(
                cr,
                f"""
                UPDATE _ir_translation
                SET name = '{model},{new_field}'
                WHERE name = '{model},{old_field}' AND type = 'model'
                """,
            )

            # Update filters
            openupgrade.logged_query(
                cr,
                f"""
                UPDATE ir_filters
                SET domain = regexp_replace(domain,
                '''?{old_field}''?', '{new_field}', 'g')
                WHERE model_id = '{model}' AND domain ~ '{old_field}'
                """,
            )
            # Update exports
            openupgrade.logged_query(
                cr,
                f"""
                UPDATE ir_exports_line iel
                SET name = '{new_field}'
                FROM ir_exports ie
                WHERE iel.name = '{old_field}' AND
                ie.id = iel.export_id AND ie.resource = '{model}'
                """,
            )
