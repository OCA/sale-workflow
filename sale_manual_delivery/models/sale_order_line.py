# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_procurement_create(self):
        for line in self:
            if (line.order_id.manual_procurement and
                    line.product_id.type != 'service'):
                return self.env['procurement.order'].browse()
            else:
                return super(SaleOrderLine, self)._action_procurement_create()
