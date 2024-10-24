# Copyright 2024 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo.api import SUPERUSER_ID, Environment


def pre_init_hook(cr):
    """
    Create the sale order invoice policy with the "product" policy (standard)
    but with a postgres query to avoid an update on all sale order records
    """
    env = Environment(cr, SUPERUSER_ID, {})
    field_spec = [
        (
            "invoice_policy",
            "sale.order",
            False,
            "selection",
            False,
            "sale_invoice_policy",
            "product",
        )
    ]
    openupgrade.add_fields(env, field_spec=field_spec)
