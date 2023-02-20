# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    @api.model
    def run_with_workflow_with_delay(self, sale_workflow):
        workflow_domain = [("workflow_process_id", "=", sale_workflow.id)]
        if sale_workflow.validate_order:
            self.with_context(
                send_order_confirmation_mail=sale_workflow.send_order_confirmation_mail,
            )._validate_sale_orders(
                safe_eval(sale_workflow.order_filter_id.domain) + workflow_domain
            )

    def run_with_workflow(self, sale_workflow):
        super_self = self.with_context(
            sale_workflow_validate_with_delay=sale_workflow.validate_order_with_delay
        )
        return super(AutomaticWorkflowJob, super_self).run_with_workflow(sale_workflow)

    def _validate_sale_orders(self, order_filter):
        if self.env.context.get("sale_workflow_validate_with_delay"):
            return
        return super()._validate_sale_orders(order_filter)

    @api.model
    def _run_with_delay_workflow_domain(self):
        return [("validate_order_with_delay", "=", True)]

    @api.model
    def run_with_delay(self):
        """Called from ir.cron"""
        sale_workflow_process = self.env["sale.workflow.process"]
        domain = self._run_with_delay_workflow_domain()
        for sale_workflow in sale_workflow_process.search(domain):
            self.run_with_workflow_with_delay(sale_workflow)
        return True
