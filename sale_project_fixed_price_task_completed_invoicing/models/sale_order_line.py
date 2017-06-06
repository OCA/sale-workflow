# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        line = super(SaleOrderLine, self).create(vals)
        if (line.state == 'sale' and not line.order_id.project_id and
                line.product_id.track_service in ('completed_task', )):
            line.order_id._create_analytic_account()
        return line

    @api.multi
    def _check_delivered_qty(self):
        for line in self:
            tasks = self.env['project.task'].search(
                [('sale_line_id', '=', line.id)])
            if len(tasks) == len(tasks.filtered('invoiceable')):
                line.qty_delivered = line.product_uom_qty
