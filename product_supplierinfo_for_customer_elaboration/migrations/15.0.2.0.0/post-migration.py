# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.m2o_to_x2m(
        env.cr,
        env["product.customerinfo"],
        "product_customerinfo",
        "elaboration_ids",
        openupgrade.get_legacy_name("elaboration_id"),
    )
