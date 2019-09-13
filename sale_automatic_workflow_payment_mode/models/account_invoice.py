# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('payment_mode_id')
    def onchange_payment_mode_set_workflow(self):
        if not self.payment_mode_id:
            return
        workflow = self.payment_mode_id.workflow_process_id
        if workflow:
            self.workflow_process_id = workflow
