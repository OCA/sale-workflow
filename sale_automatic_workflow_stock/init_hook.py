import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    # on v16 automatic_workflow_picking_filter
    # is in sale_automatic_workflow module

    old_xmlid = "sale_automatic_workflow.automatic_workflow_picking_filter"
    new_xmlid = "sale_automatic_workflow_stock.automatic_workflow_picking_filter"

    _logger.info(f"XML ID migration {old_xmlid} to {new_xmlid}")
    # it's safe to run even if old_xmlid do not exits
    openupgrade.rename_xmlids(
        env.cr,
        [
            (old_xmlid, new_xmlid),
        ],
    )
