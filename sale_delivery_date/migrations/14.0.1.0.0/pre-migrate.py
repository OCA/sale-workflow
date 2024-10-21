# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


def migrate_calendar2(cr):
    model = "stock_warehouse"
    field_names = ["calendar2_id"]
    previous_module = "sale_warehouse_calendar"
    new_module = "sale_delivery_date"
    openupgrade.update_module_moved_fields(
        cr, model, field_names, previous_module, new_module
    )


def migrate(cr, version):
    migrate_calendar2(cr)
