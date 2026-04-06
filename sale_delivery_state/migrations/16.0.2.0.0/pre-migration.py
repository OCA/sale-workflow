# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "sale_order_line", "skip_sale_delivery_state"
    ):
        _logger.info("Create sale_order_line column skip_sale_delivery_state")
        openupgrade.add_fields(
            env,
            [
                (
                    "skip_sale_delivery_state",
                    "sale.order.line",
                    "sale_order_line",
                    "boolean",
                    "boolean",
                    "sale_delivery_state",
                    "false",
                ),
            ],
        )
