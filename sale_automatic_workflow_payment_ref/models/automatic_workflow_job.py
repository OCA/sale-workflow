# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AutomaticWorkflowJob(models.Model):

    _inherit = 'automatic.workflow.job'

    @api.model
    def _prepare_invoice_account_payment_vals(self, invoice):
        vals = super(AutomaticWorkflowJob,
                     self)._prepare_invoice_account_payment_vals(invoice)
        vals['transaction_id'] = invoice.transaction_id
        return vals
