# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# Copyright 2025 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    _setup_new_columns(env.cr)


def _setup_new_columns(cr):
    if not column_exists(cr, "sale_order", "delivery_status"):
        _logger.info("Create sale_order column delivery_status")
        create_column(cr, "sale_order", "delivery_status", "varchar")
    if not column_exists(cr, "sale_order_line", "skip_sale_delivery_state"):
        _logger.info("Create sale_order_line column skip_sale_delivery_state")
        create_column(cr, "sale_order_line", "skip_sale_delivery_state", "boolean")
        cr.execute("UPDATE sale_order_line SET skip_sale_delivery_state = False")
