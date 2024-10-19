# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    workflow_process_id = fields.Many2one(
        compute="_compute_workflow_process_id", store=True, readonly=False
    )

    @api.depends("payment_mode_id")
    def _compute_workflow_process_id(self):
        for sale in self:
            if sale.payment_mode_id.workflow_process_id:
                sale.workflow_process_id = sale.payment_mode_id.workflow_process_id.id
