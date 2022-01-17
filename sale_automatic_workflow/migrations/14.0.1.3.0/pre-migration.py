# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "sale_automatic_workflow_payment_mode.automatic_workflow_payment_filter",
                "sale_automatic_workflow.automatic_workflow_payment_filter",
            ),
        ],
    )
