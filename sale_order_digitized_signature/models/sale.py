# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_signature = fields.Binary(string='Customer acceptance')

    @api.model
    def create(self, values):
        sale = super(SaleOrder, self).create(values)
        if sale.customer_signature:
            values = {'customer_signature': sale.customer_signature}
            sale._track_signature(values, 'customer_signature')
        return sale

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(SaleOrder, self).write(values)
