# -*- encoding: utf-8 -*-
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


from openerp.osv.orm import Model
import netsvc
import logging
from tools.translate import _
from contextlib import contextmanager

#Some comment about the implementation
#In order to validate the invoice the picking we have to use schedule action
#Indeed, if we directly jump the various step in the workflow of the invoice and the picking
#the sale order workflow will be broken
#The explication is "simple"
#Example with the invoice workflow
#When we are in the sale order at the step router
#a transiotion like a signal or condition will change the step of the workflow to the step 'invoice'
#the fact to enter in this step will launch the creation of the invoice
#if the invoice in directly validated and reconcilled with the payment
#the subworkflow will end and send a signal to the sale order workflow
#the problem is that the sale order workflow have not finish to apply the step invoice
#and so the signal of the subworkflow will be lost
#because the step invoice is still not finish
#The step invoice should be finish before receiving the signal
#this is meant that we can not directly validated every step of the workflow invoice_amount
#it the same with the picking workflow_method

#If my explication is not clear contact me by email and I will imporve it: sebastien.beau@akretion.com


@contextmanager
def commit_now(cr, logger, raise_error=False):
    """
    Context Manager to use in order to commit into a cursor
    correctly with a try/except method and a rollback if necessary
    :param cr cursor: cursor to commit
    :param logger logger: logger use for loging message
    :param raise_error boolean: Set to true only if you want
             to stop the process if an error occure
    """
    try:
        yield cr
    except Exception, e:
        cr.rollback()
        logger.exception(e)
        if raise_error:
            raise
    else:
        cr.commit()


class automatic_workflow_job(Model):
    """
    Scheduler that will play automatically the validation on invoice, picking...
    """
    _name = 'automatic.workflow.job'

    def run(self, cr, uid, ids=None, context=None):
        logger = logging.getLogger(__name__)
        wf_service = netsvc.LocalService("workflow")
        invoice_obj = self.pool.get('account.invoice')
        open_invoice_ids = invoice_obj.search(cr, uid, [('state', 'in', ['open'])], context=context)

        for open_invoice_id in open_invoice_ids:
            with commit_now(cr, logger) as cr:
                invoice_obj.reconcile_invoice(cr, uid, [open_invoice_id], context=context)

        invoice_ids = invoice_obj.search(cr, uid, [('state', 'in', ['draft']), ('workflow_process_id.validate_invoice', '=',True)], context=context)
        if invoice_ids:
            logger.debug(_('start to validate invoice : %s') %invoice_ids)
        for invoice_id in invoice_ids:
            with commit_now(cr, logger) as cr:
                wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                invoice_obj.reconcile_invoice(cr, uid, [invoice_id], context=context)

        picking_obj = self.pool.get('stock.picking')
        picking_ids = picking_obj.search(cr, uid, [('state', 'in', ['draft', 'confirmed', 'assigned']), ('workflow_process_id.validate_picking', '=',True)], context=context)
        if picking_ids:
            logger.debug(_('start to validate pickings : %s') %picking_ids)
            with commit_now(cr, logger) as cr:
                picking_obj.validate_picking(cr, uid, picking_ids, context=context)
        return True
