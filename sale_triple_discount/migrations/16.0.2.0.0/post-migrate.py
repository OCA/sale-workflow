# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import openupgrade


@openupgrade.logging()
def compute_discount(env):
    env["sale.order.line"].search(
        [
            "|",
            "|",
            ("discount1", "!=", 0),
            ("discount2", "!=", 0),
            ("discount3", "!=", 0),
        ]
    )
    env["sale.order.line"]._compute_discount()


@openupgrade.migrate()
def migrate(env, version):
    compute_discount(env)
