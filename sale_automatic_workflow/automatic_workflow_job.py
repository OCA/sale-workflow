# -*- coding: utf-8 -*-
###############################################################################
#
#    sale_automatic_workflow for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Copyright 2013 Camptocamp SA (Guewen Baconnier)
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
###############################################################################

"""
Some comments about the implementation

In order to validate the invoice and the picking, we have to use
scheduled actions, because if we directly jump the various steps in the
workflow of the invoice and the picking, the sale order workflow will be
broken.

The explanation is 'simple'. Example with the invoice workflow: When we
are in the sale order at the workflow router, a transition like a signal
or condition will change the step of the workflow to the step 'invoice';
this step will launch the creation of the invoice.  If the invoice is
directly validated and reconciled with the payment, the subworkflow will
end and send a signal to the sale order workflow.  The problem is that
the sale order workflow has not yet finished to apply the step 'invoice',
so the signal of the subworkflow will be lost because the step 'invoice'
is still not finished. The step invoice should be finished before
receiving the signal. This means that we can not directly validate every
steps of the workflow in the same transaction.

If my explanation is not clear, contact me by email and I will improve
it: sebastien.beau@akretion.com
"""

import logging
from contextlib import contextmanager
from openerp import models, api

_logger = logging.getLogger(__name__)


@contextmanager
def commit(cr):
    """
    Commit the cursor after the ``yield``, or rollback it if an
    exception occurs.

    Warning: using this method, the exceptions are logged then discarded.
    """
    try:
        yield
    except Exception:
        cr.rollback()
        _logger.exception('Error during an automatic workflow action.')
    else:
        cr.commit()


class AutomaticWorkflowJob(models.Model):
    """ Scheduler that will play automatically the validation of
    invoices, pickings...  """

    _name = 'automatic.workflow.job'

    @api.model
    def _get_domain_for_sale_validation(self):
        return [('state', '=', 'draft'),
                ('workflow_process_id.validate_order', '=', True)]

    @api.model
    def _validate_sale_orders(self):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search(self._get_domain_for_sale_validation())
        _logger.debug('Sale Orders to validate: %s', sales)
        for sale in sales:
            with commit(self.env.cr):
                sale.action_button_confirm()

    @api.model
    def _validate_invoices(self):
        invoice_obj = self.env['account.invoice']
        invoices = invoice_obj.search(
            [('state', 'in', ['draft']),
             ('workflow_process_id.validate_invoice', '=', True)],
        )
        _logger.debug('Invoices to validate: %s', invoices)
        for invoice in invoices:
            with commit(self.env.cr):
                invoice.signal_workflow('invoice_open')

    @api.model
    def _validate_pickings(self):
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.search(
            [('state', 'in', ['draft', 'confirmed', 'assigned']),
             ('workflow_process_id.validate_picking', '=', True)],
        )
        _logger.debug('Pickings to validate: %s', pickings)
        if pickings:
            with commit(self.env.cr):
                pickings.validate_picking()

    @api.model
    def run(self):
        """ Must be called from ir.cron """

        self._validate_sale_orders()
        self._validate_invoices()
        self._validate_pickings()
        return True
