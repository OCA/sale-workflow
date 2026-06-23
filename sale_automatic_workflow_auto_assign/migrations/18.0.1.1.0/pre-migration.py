# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # The ``priority`` field was renamed to ``auto_assign_priority``. Rename the
    # column so existing values are kept. Guarded to stay idempotent: a fresh
    # install already ships the new column, nothing to rename.
    if openupgrade.column_exists(
        env.cr, "sale_workflow_process", "priority"
    ) and not openupgrade.column_exists(
        env.cr, "sale_workflow_process", "auto_assign_priority"
    ):
        openupgrade.rename_fields(
            env,
            [
                (
                    "sale.workflow.process",
                    "sale_workflow_process",
                    "priority",
                    "auto_assign_priority",
                )
            ],
        )
