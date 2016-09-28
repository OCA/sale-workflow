# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('type_id')
    def onchange_type_id_sale_journal(self):
        if self.type_id.invoice_type_id:
            self.invoice_type_id = self.type_id.invoice_type_id.id
