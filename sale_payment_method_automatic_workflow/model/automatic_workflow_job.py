# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import models, api
from openerp.addons.sale_automatic_workflow.automatic_workflow_job import (
    commit
)


_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = 'automatic.workflow.job'

    @api.model
    def _reconcile_invoices(self):
        invoice_model = self.env['account.invoice']
        for invoice in invoice_model.search([('state', 'in', ['open'])]):
            with commit(self.env.cr):
                invoice.reconcile_invoice()

    @api.model
    def run(self):
        self._autopay()
        res = super(AutomaticWorkflowJob, self).run()
        self._reconcile_invoices()
        return res

    @api.model
    def _get_domain_for_sale_autopayment(self):
        return [('state', '=', 'draft'),
                ('workflow_process_id.autopay', '=', True)]

    @api.model
    def _autopay(self):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search(self._get_domain_for_sale_autopayment())
        _logger.debug('Sale Orders to automatically pay: %s', sales)
        for sale in sales:
            with commit(self.env.cr):
                sale.automatic_payment()
