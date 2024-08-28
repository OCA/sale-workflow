# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not column_exists(cr, "sale_order_line", "skip_sale_delivery_state"):
        _logger.info("Create sale_order_line column skip_sale_delivery_state")
        create_column(cr, "sale_order_line", "skip_sale_delivery_state", "boolean")
        cr.execute("UPDATE sale_order_line SET skip_sale_delivery_state = False")
