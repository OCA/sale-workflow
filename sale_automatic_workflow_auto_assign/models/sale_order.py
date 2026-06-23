# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        workflows = self._get_auto_assign_workflows()

        for record in records:
            if not record.workflow_process_id:
                workflow = record._get_auto_assign_workflow(workflows)
                if workflow:
                    record.workflow_process_id = workflow

        return records

    def copy(self, default=None):
        records = super().copy(default=default)
        # "copy_fallback" mode: ``create`` (above) re-derives the workflow from the
        # auto-assign rules first. Only when no workflow could be auto-assigned do we
        # fall back to copying the origin's workflow. The "copy" (always) and "no_copy"
        # modes are fully handled by ``copy_data`` in ``sale_automatic_workflow``.
        if self._get_sale_workflow_copy_mode() == "copy_fallback":
            for new_order, origin in zip(records, self, strict=False):
                if not new_order.workflow_process_id:
                    new_order.workflow_process_id = origin.workflow_process_id
        return records

    def _get_auto_assign_workflows(self):
        return self.env["sale.workflow.process"].search(
            [("auto_assign", "=", True)], order="auto_assign_priority ASC"
        )

    def _get_auto_assign_workflow(self, workflows):
        workflows.fetch(["auto_assign_domain"])
        for workflow in workflows:
            try:
                if self.filtered_domain(safe_eval(workflow.auto_assign_domain or "[]")):
                    return workflow
            except KeyError as exc:
                _logger.warning(
                    "Invalid domain '%s' for workflow '%s' "
                    "on sale order %s. Missing key: %s",
                    workflow.auto_assign_domain,
                    workflow.display_name,
                    self.name,
                    str(exc),
                )
                continue
