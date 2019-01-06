# -*- coding: utf-8 -*-
# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if not self.partner_id:
            self.incoterm = False
            return res
        self.incoterm = self.partner_id.sale_incoterm_id
        return res
