# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    """Extend to add stock related workflow."""

    _inherit = "sale.order"

    @api.onchange("workflow_process_id")
    def _onchange_workflow_process_id(self):
        """Override to add stock related workflow."""
        super()._onchange_workflow_process_id()
        workflow = self.workflow_process_id
        if workflow.picking_policy:
            self.picking_policy = workflow.picking_policy
