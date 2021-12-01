# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


MERGED_MODULE_NAMES = (
    "sale_warehouse_calendar",
    "sale_cutoff_time_delivery",
    "sale_partner_delivery_window",
    "sale_partner_cutoff_delivery_window",
)


def pre_init_hook(cr):
    """Since 4 modules (sale_warehouse_calendar, sale_cutoff_time_delivery,
    sale_partner_delivery_window, sale_partner_cutoff_delivery_window)
    are merged into this one, we have to set the previous modules as
    uninstalled, as well as we need to update the module names in ir_model_data
    """
    query_installed = """
        SELECT id FROM ir_module_module
        WHERE name IN %s and state IN ('installed', 'to upgrade')
    """
    cr.execute(query_installed, (MERGED_MODULE_NAMES,))
    modules_installed = any(row[0] for row in cr.fetchall())
    if modules_installed:
        modules_to_merge = [
            (merged_module_name, "sale_delivery_date")
            for merged_module_name in MERGED_MODULE_NAMES
        ]
        openupgrade.update_module_names(cr, modules_to_merge, merge_modules=True)
