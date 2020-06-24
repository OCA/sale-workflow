# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.safe_eval import safe_eval
from odoo.addons.sale_automatic_workflow.models.automatic_workflow_job import\
    savepoint
import logging
_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):

    _inherit = 'automatic.workflow.job'

    @api.model
    def _validate_purchase_orders(self, sale_filter, po_filter):
        sales = self.env['sale.order'].search(sale_filter)
        _logger.debug('Sale Orders from which validate Purchase Orders: %s',
                      sales.ids)
        for sale in sales.filtered(lambda s: s.procurement_group_id.id):
            domain = list(po_filter)  # takes a copy of the original domain
            domain.append(('group_id', '=', sale.procurement_group_id.id))
            purchase_orders = self.env['purchase.order'].search(domain)
            if not purchase_orders:
                continue
            with savepoint(self.env.cr):
                purchase_orders.button_confirm()

    @api.model
    def run_with_workflow(self, sale_workflow):
        super(AutomaticWorkflowJob, self).run_with_workflow(sale_workflow)
        workflow_domain = [('workflow_process_id', '=', sale_workflow.id)]
        if sale_workflow.validate_purchase_mto:
            self._validate_purchase_orders(
                safe_eval(sale_workflow.purchase_order_mto_filter_id.domain) +
                workflow_domain,
                safe_eval(sale_workflow.purchase_order_mto_purchase_filter_id.
                          domain))
