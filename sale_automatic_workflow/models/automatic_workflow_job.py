# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager
from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


@contextmanager
def savepoint(cr):
    """ Open a savepoint on the cursor, then yield.

    Warning: using this method, the exceptions are logged then discarded.
    """
    try:
        with cr.savepoint():
            yield
    except Exception:
        _logger.exception('Error during an automatic workflow action.')


class AutomaticWorkflowJob(models.Model):
    """ Scheduler that will play automatically the validation of
    invoices, pickings...  """

    _name = 'automatic.workflow.job'
    _description = (
        'Scheduler that will play automatically the validation of'
        ' invoices, pickings...'
    )

    def _do_validate_sale_order(self, sale):
        """Validate a sales order"""
        with savepoint(self.env.cr):
            sale.with_context(
                force_company=sale.company_id.id
            ).action_confirm()

    @api.model
    def _validate_sale_orders(self, order_filter):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search(order_filter)
        _logger.debug('Sale Orders to validate: %s', sales.ids)
        for sale in sales:
            self._do_validate_sale_order(sale)

    def _do_create_invoice(self, sale):
        """Create an invoice for a sales order"""
        with savepoint(self.env.cr):
            payment = self.env['sale.advance.payment.inv'].create(
                {'advance_payment_method': 'all'})
            payment.with_context(
                active_ids=sale.ids,
                force_company=sale.company_id.id
            ).create_invoices()

    @api.model
    def _create_invoices(self, create_filter):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search(create_filter)
        _logger.debug('Sale Orders to create Invoice: %s', sales.ids)
        for sale in sales:
            self._do_create_invoice(sale)

    def _do_validate_invoice(self, invoice):
        """Validate an invoice"""
        with savepoint(self.env.cr):
            try:
                invoice.with_context(
                    force_company=invoice.company_id.id
                ).action_invoice_open()
            except Exception:
                _logger.exception('Error on validating invoice {}'.format(invoice.id))
                raise

    @api.model
    def _validate_invoices(self, validate_invoice_filter):
        invoice_obj = self.env['account.invoice']
        invoices = invoice_obj.search(validate_invoice_filter)
        _logger.debug('Invoices to validate: %s', invoices.ids)
        for invoice in invoices:
            self._do_validate_invoice(invoice)

    def _do_validate_picking(self, picking):
        """Validate a stock.picking"""
        with savepoint(self.env.cr):
            picking.validate_picking()

    @api.model
    def _validate_pickings(self, picking_filter):
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.search(picking_filter)
        _logger.debug('Pickings to validate: %s', pickings.ids)
        for picking in pickings:
            self._do_validate_picking(picking)

    def _do_sale_done(self, sale):
        """Set a sales order to done"""
        with savepoint(self.env.cr):
            sale.with_context(
                force_company=sale.company_id.id
            ).action_done()

    @api.model
    def _sale_done(self, sale_done_filter):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search(sale_done_filter)
        _logger.debug('Sale Orders to done: %s', sales.ids)
        for sale in sales:
            self._do_sale_done(sale)

    @api.model
    def run_with_workflow(self, sale_workflow):
        workflow_domain = [('workflow_process_id', '=', sale_workflow.id)]
        if sale_workflow.validate_order:
            self._validate_sale_orders(
                safe_eval(sale_workflow.order_filter_id.domain) +
                workflow_domain)
        if sale_workflow.validate_picking:
            self._validate_pickings(
                safe_eval(sale_workflow.picking_filter_id.domain) +
                workflow_domain)
        if sale_workflow.create_invoice:
            self._create_invoices(
                safe_eval(sale_workflow.create_invoice_filter_id.domain) +
                workflow_domain)
        if sale_workflow.validate_invoice:
            self._validate_invoices(
                safe_eval(
                    sale_workflow.validate_invoice_filter_id.domain) +
                workflow_domain)
        if sale_workflow.sale_done:
            self._sale_done(
                safe_eval(
                    sale_workflow.sale_done_filter_id.domain) +
                workflow_domain)

    @api.model
    def run(self):
        """ Must be called from ir.cron """
        sale_workflow_process = self.env['sale.workflow.process']
        for sale_workflow in sale_workflow_process.search([]):
            self.run_with_workflow(sale_workflow)
        return True
