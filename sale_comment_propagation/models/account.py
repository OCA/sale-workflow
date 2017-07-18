# -*- coding: utf-8 -*-
# Copyright 2015 Ainara Galdona - AvanzOSC
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_comment = fields.Text(string='Internal comments')

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            self.sale_comment = self.partner_id._get_invoice_comments()
        return res
