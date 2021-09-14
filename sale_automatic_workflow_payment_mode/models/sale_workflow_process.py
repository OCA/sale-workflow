# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    @api.model
    def _default_payment_filter_id(self):
        xmlid = "sale_automatic_workflow_payment_mode.automatic_workflow_payment_filter"
        try:
            return self.env.ref(xmlid)
        except ValueError:
            return self._default_payment_filter_id()
