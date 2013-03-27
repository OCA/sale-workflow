# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_automatic_workflow for OpenERP                                        #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################


import logging
from openerp.osv import orm
from openerp import netsvc
from openerp.tools.translate import _
from framework_helpers.context_managers import new_cursor, commit_now

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

_logger = logging.getLogger(__name__)


class automatic_workflow_job(orm.Model):
    """ Scheduler that will play automatically the validation of
    invoices, pickings...  """
    _name = 'automatic.workflow.job'

    def run(self, cr, uid, ids=None, context=None):
        wf_service = netsvc.LocalService("workflow")
        invoice_obj = self.pool.get('account.invoice')
        picking_obj = self.pool.get('stock.picking.out')

        with new_cursor(cr, _logger) as cr:
            open_invoice_ids = invoice_obj.search(cr, uid,
                                                  [('state', 'in', ['open'])],
                                                  context=context)
            for invoice_id in open_invoice_ids:
                with commit_now(cr, _logger) as cr:
                    invoice_obj.reconcile_invoice(cr, uid,
                                                  [invoice_id],
                                                  context=context)

            invoice_ids = invoice_obj.search(
                cr, uid,
                [('state', 'in', ['draft']),
                 ('workflow_process_id.validate_invoice', '=', True)],
                context=context)
            if invoice_ids:
                _logger.debug('Start to validate invoices: %s', invoice_ids)
            for invoice_id in invoice_ids:
                with commit_now(cr, _logger) as cr:
                    wf_service.trg_validate(uid, 'account.invoice',
                                            invoice_id, 'invoice_open', cr)
                with commit_now(cr, _logger) as cr:
                    invoice_obj.reconcile_invoice(cr, uid, [invoice_id],
                                                  context=context)

            picking_ids = picking_obj.search(
                cr, uid,
                [('state', 'in', ['draft', 'confirmed', 'assigned']),
                 ('workflow_process_id.validate_picking', '=', True)],
                context=context)
            if picking_ids:
                _logger.debug('Start to validate pickings: %s', picking_ids)
                with commit_now(cr, _logger) as cr:
                    picking_obj.validate_picking(cr, uid, picking_ids,
                                                 context=context)
        return True
