# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _do_force_invoice_orders(self, sale):
        sale.write({"force_invoiced": True})
        return f"{sale.display_name} set to force invoice successfully"

    @api.model
    def _force_invoice_orders(self, order_filter):
        sales = self.env["sale.order"].search(order_filter)
        for sale in sales:
            try:
                with self.env.cr.savepoint():
                    self._do_force_invoice_orders(sale.with_company(sale.company_id))
            except Exception:
                _logger.exception(
                    "Error during automatic workflow action for sale %s",
                    sale.display_name,
                )

    @api.model
    def run_with_workflow(self, sale_workflow):
        workflow_domain = [("workflow_process_id", "=", sale_workflow.id)]
        if sale_workflow.force_invoice:
            self._force_invoice_orders(
                safe_eval(sale_workflow.force_invoice_order_filter_id.domain)
                + workflow_domain
            )
        return super().run_with_workflow(sale_workflow)
