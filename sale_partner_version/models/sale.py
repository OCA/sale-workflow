# -*- coding: utf-8 -*-
# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        address_fields = ['partner_shipping_id', 'partner_invoice_id']
        for order in self:
            for address_field in address_fields:
                order[address_field] = order[address_field].get_address_version()
        return super(SaleOrder, self).action_confirm()
