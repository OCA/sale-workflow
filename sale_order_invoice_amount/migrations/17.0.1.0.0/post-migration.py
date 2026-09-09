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

    openupgrade.rename_fields(env=cr, field_spec=_field_renames, no_deep=True)
