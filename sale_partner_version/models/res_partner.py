# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _version_need(self):
        res = super(ResPartner, self)._version_need()
        if not res:
            domain = [
                '&', '|', '|',
                ('partner_id', '=', self.id),
                ('partner_shipping_id', '=', self.id),
                ('partner_invoice_id', '=', self.id),
                ('state', 'not in', ['draft', 'cancel'])
            ]
            so_count = self.env['sale.order'].search_count(domain)
            return bool(so_count)

        return res

    def _version_impacted_tables(self):
        res = super(ResPartner, self)._version_impacted_tables()
        tables = ['sale_order', 'sale_order_line', 'account_invoice',
                  'account_invoice_line', 'account_move', 'account_move_line']
        res.extend(tables)
        return res
