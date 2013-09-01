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
from contextlib import contextmanager
from openerp.osv import orm
from openerp import pooler
from openerp import netsvc

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


@contextmanager
def commit(cr):
    """
    Commit the cursor after the ``yield``, or rollback it if an
    exception occurs.

    Warning: using this method, the exceptions are logged then discarded.
    """
    try:
        yield
    except Exception, e:
        cr.rollback()
        _logger.exception('Error during an automatic workflow action.')
    else:
        cr.commit()


class automatic_workflow_job(orm.Model):
    """ Scheduler that will play automatically the validation of
    invoices, pickings...  """
    _name = 'automatic.workflow.job'

    def _validate_sale_orders(self, cr, uid, context=None):
        wf_service = netsvc.LocalService("workflow")
        sale_obj = self.pool.get('sale.order')
        sale_ids = sale_obj.search(
            cr, uid,
            [('state', '=', 'draft'),
             ('workflow_process_id.validate_order', '=', True),
             ('exceptions_ids', '=', False)],
            context=context)
        _logger.debug('Sale Orders to validate: %s', sale_ids)
        for sale_id in sale_ids:
            with commit(cr):
                wf_service.trg_validate(uid, 'sale.order',
                                        sale_id, 'order_confirm', cr)

    def _reconcile_invoices(self, cr, uid, ids=None, context=None):
        invoice_obj = self.pool.get('account.invoice')
        if ids is None:
            ids = invoice_obj.search(cr, uid,
                                     [('state', 'in', ['open'])],
                                     context=context)
        for invoice_id in ids:
            with commit(cr):
                invoice_obj.reconcile_invoice(cr, uid,
                                              [invoice_id],
                                              context=context)

    def _validate_invoices(self, cr, uid, context=None):
        wf_service = netsvc.LocalService("workflow")
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(
            cr, uid,
            [('state', 'in', ['draft']),
             ('workflow_process_id.validate_invoice', '=', True)],
            context=context)
        _logger.debug('Invoices to validate: %s', invoice_ids)
        for invoice_id in invoice_ids:
            with commit(cr):
                wf_service.trg_validate(uid, 'account.invoice',
                                        invoice_id, 'invoice_open', cr)

    def _validate_pickings(self, cr, uid, context=None):
        picking_obj = self.pool.get('stock.picking')
        picking_out_obj = self.pool.get('stock.picking.out')
        # We search on stock.picking (using the type) rather than
        # stock.picking.out because the ORM seems bugged and can't
        # search on stock_picking_out.workflow_process_id.
        # Later, we'll call `validate_picking` on stock.picking.out
        # because anyway they have the same ID and the call will be at
        # the correct object level.
        picking_ids = picking_obj.search(
            cr, uid,
            [('state', 'in', ['draft', 'confirmed', 'assigned']),
             ('workflow_process_id.validate_picking', '=', True),
             ('type', '=', 'out')],
            context=context)
        _logger.debug('Pickings to validate: %s', picking_ids)
        if picking_ids:
            with commit(cr):
                picking_out_obj.validate_picking(cr, uid,
                                                 picking_ids,
                                                 context=context)

    def run(self, cr, uid, ids=None, context=None):
        """ Must be called from ir.cron """

        self._validate_sale_orders(cr, uid, context=context)
        self._validate_invoices(cr, uid, context=context)
        self._reconcile_invoices(cr, uid, context=context)
        self._validate_pickings(cr, uid, context=context)
        return True
