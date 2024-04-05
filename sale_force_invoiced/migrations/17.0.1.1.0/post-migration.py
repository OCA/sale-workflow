# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    val_users = [
        (4, user.id) for user in env.ref("sales_team.group_sale_manager").users
    ]
    if val_users:
        env.ref("sale_force_invoiced.group_force_invoiced").write({"users": val_users})
    _logger.info("Assign `group_force_invoiced` to all sale administrators")
