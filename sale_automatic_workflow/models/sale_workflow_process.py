# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.model
    def _default_filter(self, xmlid):
        record = self.env.ref(xmlid, raise_if_not_found=False)
        if record:
            return record
        return self.env['ir.filters'].browse()

    name = fields.Char()
    picking_policy = fields.Selection(
        selection=[('direct', 'Deliver each product when available'),
                   ('one', 'Deliver all products at once')],
        string='Shipping Policy',
        default='direct',
    )
    validate_order = fields.Boolean(string='Validate Order')
    order_filter_domain = fields.Char(
        string='Order Filter Domain',
        default="[('state', '=', 'draft')]"
    )
    create_invoice = fields.Boolean(string='Create Invoice')
    create_invoice_filter_domain = fields.Char(
        string='Create Invoice Filter Domain',
        default="[('state','in',['sale','done']),"
        "('invoice_status','=','to invoice')]"
    )
    validate_invoice = fields.Boolean(string='Validate Invoice')
    validate_invoice_filter_domain = fields.Char(
        string='Validate Invoice Filter Domain',
        default="[('state', '=', 'draft')]"
    )
    validate_picking = fields.Boolean(string='Confirm and Transfer Picking')
    picking_filter_domain = fields.Char(
        string='Picking Filter Domain',
        default="[('state', 'in', ['draft', 'confirmed', 'assigned'])]"
    )
    invoice_date_is_order_date = fields.Boolean(
        string='Force Invoice Date',
        help="When checked, the invoice date will be "
             "the same than the order's date"
    )

    invoice_service_delivery = fields.Boolean(
        string='Invoice Service on delivery',
        help="If this box is checked, when the first invoice is created "
             "The service sale order lines will be included and will be "
             "marked as delivered"
    )
    sale_done = fields.Boolean(string='Sale Done')
    sale_done_filter_domain = fields.Char(
        string='Sale Done Filter Domain',
        default="[('state', '=', 'sale'),('invoice_status','=','invoiced'),"
                "('all_qty_delivered', '=', True)]"
    )
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
        default=lambda self: self._default_filter(
            'sale_automatic_workflow.automatic_workflow_order_filter'
        )
    )
    picking_filter_id = fields.Many2one(
        'ir.filters',
        string='Picking Filter',
        default=lambda self: self._default_filter(
            'sale_automatic_workflow.automatic_workflow_picking_filter'
        )
    )
    create_invoice_filter_id = fields.Many2one(
        'ir.filters',
        string='Create Invoice Filter',
        default=lambda self: self._default_filter(
            'sale_automatic_workflow.automatic_workflow_create_invoice_filter'
        )
    )
    validate_invoice_filter_id = fields.Many2one(
        'ir.filters',
        string='Validate Invoice Filter',
        default=lambda self: self._default_filter(
            'sale_automatic_workflow.'
            'automatic_workflow_validate_invoice_filter'
        )
    )
    sale_done_filter_id = fields.Many2one(
        'ir.filters',
        string='Sale Done Filter',
        default=lambda self: self._default_filter(
            'sale_automatic_workflow.automatic_workflow_sale_done_filter'
        )
    )

    @api.onchange('order_filter_id')
    def onchange_order_filter_id(self):
        if self.order_filter_id:
            self.order_filter_domain = self.order_filter_id.domain

    @api.onchange('picking_filter_id')
    def onchange_picking_filter_id(self):
        if self.picking_filter_id:
            self.picking_filter_domain = self.picking_filter_id.domain

    @api.onchange('create_invoice_filter_id')
    def onchange_create_invoice_filter_id(self):
        domain = self.create_invoice_filter_id.domain
        if self.create_invoice_filter_id:
            self.create_invoice_filter_domain = domain

    @api.onchange('validate_invoice_filter_id')
    def onchange_validate_invoice_filter_id(self):
        domain = self.validate_invoice_filter_id.domain
        if self.validate_invoice_filter_id:
            self.validate_invoice_filter_domain = domain

    @api.onchange('sale_done_filter_id')
    def onchange_sale_done_filter_id(self):
        if self.sale_done_filter_id:
            self.sale_done_filter_domain = self.sale_done_filter_id.domain
