# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    workflow_process_id = fields.Many2one(
        comodel_name='sale.workflow.process',
        string='Automatic Workflow'
    )
