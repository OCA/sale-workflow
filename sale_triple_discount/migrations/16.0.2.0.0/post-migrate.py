# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.logging()
def compute_discount(env):
    lines_with_discount = env["sale.order.line"].search(
        [
            "|",
            "|",
            ("discount1", "!=", 0),
            ("discount2", "!=", 0),
            ("discount3", "!=", 0),
        ]
    )
    lines_with_discount._compute_discount_consolidated()


@openupgrade.migrate()
def migrate(env, version):
    compute_discount(env)
