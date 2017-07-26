# -*- coding: utf-8 -*-
# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    requested_date = fields.Datetime()

    @api.multi
    def write(self, vals):
        for line in self:
            if not line.requested_date and line.order_id.requested_date and\
                    'requested_date' not in vals:
                vals.update({
                    'requested_date': line.order_id.requested_date
                })
        return super(SaleOrderLine, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if res.order_id.requested_date and not res.requested_date:
            res.write({'requested_date': res.order_id.requested_date})
        return res

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        vals = super(SaleOrderLine, self).\
            _prepare_order_line_procurement(group_id)
        if self.requested_date:
            vals.update({'date_planned': self.requested_date})
        return vals
