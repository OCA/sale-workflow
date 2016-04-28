# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    workflow_process_id = fields.Many2one(
        comodel_name='sale.workflow.process',
        string='Sale Workflow Process'
    )
    # TODO propose a merge to add this field by default in account module
    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        relation='sale_order_invoice_rel',
        column1='invoice_id',
        column2='order_id',
        string='Sale Orders'
    )
