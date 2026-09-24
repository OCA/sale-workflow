# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(env):
    fields_spec = [
        (
            "base_price",
            "sale.order.line",
            False,
            "float",
            "float",
            "sale_order_line_base_price_and_has_discount",
        )
    ]
    openupgrade.add_fields(env, field_spec=fields_spec)

    # Don't fill in the base price as it is impossible to be
    # sure of the pricelists configuration before.
