# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    """Extend to add stock related workflow."""

    _inherit = "sale.order"

    picking_policy = fields.Selection(
        compute="_compute_picking_policy", store=True, readonly=False
    )

    def _depends_picking_policy(self):
        depends = []
        if hasattr(super(), "_depends_picking_policy"):
            depends = super()._depends_picking_policy()
        depends.append("workflow_process_id")
        return depends

    @api.depends(lambda self: self._depends_picking_policy())
    def _compute_picking_policy(self):
        res = None
        if hasattr(super(), "_compute_picking_policy"):
            res = super()._compute_picking_policy()
        for order in self.filtered("workflow_process_id"):
            order_workflow_process = order.workflow_process_id
            if order_workflow_process.picking_policy:
                order.picking_policy = order_workflow_process.picking_policy
        return res
