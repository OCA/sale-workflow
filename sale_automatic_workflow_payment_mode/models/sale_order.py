# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    workflow_process_id = fields.Many2one(
        compute="_compute_payment_mode", store=True, readonly=False
    )

    @api.depends("partner_id", "company_id")
    def _compute_payment_mode(self):
        super()._compute_payment_mode()
        for sale in self:
            if sale.payment_mode_id.workflow_process_id:
                sale.workflow_process_id = sale.payment_mode_id.workflow_process_id.id
            else:
                sale.workflow_process_id = False
