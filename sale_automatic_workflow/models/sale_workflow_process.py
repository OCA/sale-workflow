# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    """ A workflow process is the setup of the automation of a sales order.

    Each sales order can be linked to a workflow process.
    Then, the options of the workflow will change how the sales order
    behave, and how it is automatized.

    A workflow process may be linked with a Sales payment method, so
    each time a payment method is used, the workflow will be applied.
    """
    _name = "sale.workflow.process"
    _description = "Sale Workflow Process"

    name = fields.Char()
    picking_policy = fields.Selection(
        selection=[('direct', 'Deliver each product when available'),
                   ('one', 'Deliver all products at once')],
        string='Shipping Policy',
        default='direct',
    )
    validate_order = fields.Boolean(string='Validate Order')
#     order_filter = fields.Text(string='Order Filter')
    create_invoice = fields.Boolean(string='Create Invoice')
#     create_invoice_filter = fields.Text(string='Create Invoice Filter')
    validate_invoice = fields.Boolean(string='Validate Invoice')
#     validate_invoice_filter = fields.Text(string='Validate Invoice Filter')
    validate_picking = fields.Boolean(string='Confirm and Transfer Picking')
#     picking_filter = fields.Text(string='Picking Filter')
    invoice_date_is_order_date = fields.Boolean(
        string='Force Invoice Date',
        help="When checked, the invoice date will be "
             "the same than the order's date"
    )
    register_payment = fields.Boolean(string='Register Payment')
#     payment_filter = fields.Text(string='Payment Filter')
    sale_done = fields.Boolean(string='Sale Done')
#     sale_done_filter = fields.Text(string='Sale Done Filter')
    warning = fields.Text(
        'Warning Message', translate=True,
        help='If set, displays the message when an user'
        'selects the process on a sale order')
    team_id = fields.Many2one(
        comodel_name='crm.team',
        string='Sales Team'
    )
    property_journal_id = fields.Many2one(
        comodel_name='account.journal',
        company_dependent=True,
        string='Sales Journal',
        help='Set default journal to use on invoice'
    )
    order_filter_id = fields.Many2one(
        'ir.filters',
        string='Order Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow.automatic_workflow_order_filter')
    )
    picking_filter_id = fields.Many2one(
        'ir.filters',
        string='Picking Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow.automatic_workflow_picking_filter')
    )
    create_invoice_filter_id = fields.Many2one(
        'ir.filters',
        string='Create Invoice Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow.automatic_workflow_create_invoice_filter')
    )
    validate_invoice_filter_id = fields.Many2one(
        'ir.filters',
        string='Validate Invoice Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow.'
            'automatic_workflow_validate_invoice_filter')
    )
    payment_filter_id = fields.Many2one(
        'ir.filters',
        string='Payment Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow.automatic_workflow_payment_filter')
    )
    sale_done_filter_id = fields.Many2one(
        'ir.filters',
        string='Sale Done Filter',
        default=lambda self: self.env.ref(
            'sale_automatic_workflow.automatic_workflow_sale_done_filter')
    )
