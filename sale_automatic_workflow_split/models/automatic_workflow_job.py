# Copyright 2017-2019 Camptocamp SA

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class AutomaticWorkflowJob(models.Model):
    _inherit = 'automatic.workflow.job'

    def _each_workflow(self):
        for workflow in self.env['sale.workflow.process'].search([]):
            domain = [('workflow_process_id', '=', workflow.id)]
            yield workflow, domain

    @api.model
    def run_validate_order(self):
        for workflow, domain in self._each_workflow():
            if workflow.validate_order:
                self._validate_sale_orders(
                    safe_eval(workflow.order_filter_id.domain) + domain
                )

    @api.model
    def run_validate_picking(self):
        for workflow, domain in self._each_workflow():
            if workflow.validate_pickings:
                self._validate_pickings(
                    safe_eval(workflow.picking_filter_id.domain) + domain
                )

    @api.model
    def run_create_invoice(self):
        for workflow, domain in self._each_workflow():
            if workflow.create_invoice:
                self._create_invoices(
                    safe_eval(workflow.create_invoice_filter_id.domain)
                    + domain
                )

    @api.model
    def run_validate_invoice(self):
        for workflow, domain in self._each_workflow():
            if workflow.validate_invoice:
                self._validate_invoices(
                    safe_eval(workflow.validate_invoice_filter_id.domain)
                    + domain
                )

    @api.model
    def run_sale_done(self):
        for workflow, domain in self._each_workflow():
            if workflow.sale_done:
                self._sale_done(
                    safe_eval(workflow.sale_done_filter_id.domain) + domain
                )
