# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("payment_mode_id")
    def onchange_payment_mode_set_workflow(self):
        pay_mode = self.payment_mode_id
        workflow = pay_mode.workflow_process_id if pay_mode else False
        self.workflow_process_id = workflow
