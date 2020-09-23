# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.sale_automatic_workflow.models.automatic_workflow_job import (
    savepoint)

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    """Extend to implement automatic work-flows for stock."""

    _inherit = "automatic.workflow.job"

    @api.model
    def _validate_pickings(self, picking_filter):
        picking_obj = self.env["stock.picking"]
        pickings = picking_obj.search(picking_filter)
        _logger.debug("Pickings to validate: %s", pickings.ids)
        for picking in pickings:
            with savepoint(self.env.cr):
                picking.validate_picking()

    @api.model
    def run_with_workflow(self, sale_workflow):
        """Override to add stock picking validation."""
        super().run_with_workflow(sale_workflow)
        workflow_domain = [("workflow_process_id", "=", sale_workflow.id)]
        if sale_workflow.validate_picking:
            self._validate_pickings(
                safe_eval(
                    sale_workflow.picking_filter_id.domain) + workflow_domain
            )
