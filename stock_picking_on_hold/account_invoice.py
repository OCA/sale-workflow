# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def confirm_paid(self):
        """
        When an invoice is paid
        a picking that is hold until payment may need a status check.
        """
        res = super(AccountInvoice, self).confirm_paid()
        # collect all pickings to check
        pickings_to_check = self.env['stock.picking']
        for invoice in self:
            for sale in invoice.sale_ids:
                for picking in sale.picking_ids:
                    if picking.state == 'hold':
                        pickings_to_check += picking
        # trigger availability check
        pickings_to_check.action_assign()
        return res
